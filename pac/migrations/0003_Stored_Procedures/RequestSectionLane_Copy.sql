CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLane_Copy] (
    @SourceRequestSectionLaneID BIGINT,
    @DestinationRequestSectionID BIGINT,
    @UpdatedBy VARCHAR(100),
    @CopiedRequestSectionLaneID BIGINT OUTPUT
)
AS
SET ANSI_NULLS ON
SET QUOTED_IDENTIFIER ON
BEGIN

    DECLARE @ERROR1 INT;
    DECLARE @ROWCOUNT1 INT;
    DECLARE @SourceRequestSectionID BIGINT;
    DECLARE @DuplicateCount INT = 0;
    DECLARE @OriginID BIGINT;
    DECLARE @OriginTypeID BIGINT;
    DECLARE @DestinationID BIGINT;
    DECLARE @DestinationTypeID BIGINT;
    DECLARE @NewLaneIDs table
    (
        [RequestSectionLaneID]  BIGINT  NOT NULL
    )

    SELECT @SourceRequestSectionID = rsl.RequestSectionID
        FROM dbo.RequestSectionLane rsl
        WHERE RequestSectionLaneID = @SourceRequestSectionLaneID;

    IF @SourceRequestSectionID = @DestinationRequestSectionID BEGIN
        RAISERROR('Request Lane cannot be inserted into the same Section', 16, 1);
        SET @CopiedRequestSectionLaneID = -1;
        RETURN;
    END

    SELECT @OriginID = OriginID, @OriginTypeID = OriginTypeID, @DestinationID = @DestinationID, @DestinationTypeID = DestinationTypeID
    FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = @SourceRequestSectionLaneID;
    SELECT @DuplicateCount = count(*)
    FROM dbo.RequestSectionLane
    WHERE OriginID = @OriginID AND OriginTypeID = @OriginTypeID AND DestinationID = DestinationID AND @DestinationTypeID = @DestinationTypeID
    AND IsActive = 1 AND RequestSectionID = @DestinationRequestSectionID;

    IF @DuplicateCount > 0 BEGIN
        RAISERROR('Request Lane would be a duplicate in the new Section', 16, 1)
        SET @CopiedRequestSectionLaneID = -2;
        RETURN;
    END

    BEGIN TRANSACTION
    INSERT INTO dbo.RequestSectionLane
        ([IsActive],[IsInactiveViewable],[RequestSectionID],
            [IsPublished],[IsEdited],[IsDuplicate],[IsBetween],
            [OriginTypeID],[OriginID],[DestinationTypeID],[DestinationID],
            [Cost],[DoNotMeetCommitment],[Commitment],[CustomerRate],[CustomerDiscount],[DrRate],[PartnerRate],[PartnerDiscount],[Profitability],
            [PickupCount],[DeliveryCount],[DockAdjustment],[Margin],[Density],[PickupCost],[DeliveryCost],
            [AccessorialsValue],[AccessorialsPercentage],[IsFlagged],[RequestSectionLaneSourceID],[Deficit],[EmbeddedCost],[ImpactPercentage]
        )
    OUTPUT INSERTED.[RequestSectionLaneID]
    INTO @NewLaneIDs
        (
        [RequestSectionLaneID]
        )
    SELECT 1,1, @DestinationRequestSectionID,
            rsl.IsPublished,rsl.IsEdited,rsl.IsDuplicate,rsl.IsBetween,
            rsl.OriginTypeID,rsl.OriginID,rsl.DestinationTypeID,rsl.DestinationID,
            rsl.Cost,rsl.DoNotMeetCommitment,rsl.Commitment,rsl.CustomerRate,rsl.CustomerDiscount,rsl.DrRate,rsl.PartnerRate,rsl.PartnerDiscount,rsl.Profitability,
            rsl.PickupCount,rsl.DeliveryCount,rsl.DockAdjustment,rsl.Margin,rsl.Density,rsl.PickupCost,rsl.DeliveryCost,
            rsl.AccessorialsValue,rsl.AccessorialsPercentage,rsl.IsFlagged,rsl.RequestSectionLaneSourceID,rsl.Deficit,rsl.EmbeddedCost,rsl.ImpactPercentage
        FROM dbo.RequestSectionLane rsl WHERE rsl.RequestSectionLaneID = @SourceRequestSectionLaneID;


    SELECT TOP(1) @CopiedRequestSectionLaneID = RequestSectionLaneID FROM @NewLaneIDs;

    -- add a history record for the new row
    EXEC dbo.[Audit_Record] @TableName = 'RequestSectionLane', @PrimaryKeyValue = @CopiedRequestSectionLaneID, @UpdatedBy = @UpdatedBy;

    COMMIT TRANSACTION
END
