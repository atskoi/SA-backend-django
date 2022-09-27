CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLane_Insert]
	@RequestSectionID BIGINT,
	@OriginTypeID BIGINT,
    @OriginTypeName NVARCHAR(50) = null,
	@OriginID BIGINT,
	@DestinationTypeID BIGINT,
    @DestinationTypeName NVARCHAR(50) = null,
	@DestinationID BIGINT,
	@IsBetween BIT,
	@Flagged BIT = 0,
	@RequestSectionLaneSourceID BIGINT,
	@RequestSectionLaneID BIGINT OUTPUT,
    @Deficit NVARCHAR(max) = null,
    @EmbeddedCost NVARCHAR(max) = null,
    @ImpactPercentage NVARCHAR(max) = null

AS
SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ROWCOUNT1 INT

DECLARE @RequestSectionLane table
(
    [RequestSectionLaneID]  BIGINT  NOT NULL
)

IF @OriginTypeID = 0 -- get the originTypeId if provided by name
    IF @OriginTypeName IS NULL
        RETURN -1; -- cannot complete this request
    ELSE
        SELECT @OriginTypeID = PointTypeID FROM dbo.PointType where PointTypeName = @OriginTypeName;
IF @DestinationTypeID = 0 -- get the originTypeId if provided by name
    IF @DestinationTypeName IS NULL
        RETURN -1; -- cannot complete this request
    ELSE
        SELECT @DestinationTypeID = PointTypeID FROM dbo.PointType where PointTypeName = @DestinationTypeName;

BEGIN TRAN

DECLARE @WeightBreak NVARCHAR(max);
DECLARE @Cost NVARCHAR(max);
SELECT @WeightBreak = wb.Levels
FROM dbo.RequestSection rs
INNER JOIN dbo.WeightBreakHeader wb ON wb.WeightBreakHeaderID = rs.WeightBreakHeaderID
	WHERE RequestSectionID = @RequestSectionID;
-- build out a default Cost value based on the WeightBreakHeaders
IF @WeightBreak IS NOT NULL
    SELECT @Cost = CONCAT('{',STRING_AGG(CONCAT('"',LevelName, '"', ':0'), ','), '}') FROM (
    SELECT JSON_VALUE(value, '$.LevelName') LevelName
    FROM OPENJSON(@WeightBreak)
    ) wb_values;
ELSE
    SET @Cost = '';

INSERT INTO dbo.RequestSectionLane
	(
		[IsActive],
		[IsInactiveViewable],
		[RequestSectionID],
		[IsPublished],
		[IsEdited],
		[IsDuplicate],
		[IsBetween],
        [OriginTypeID],
        [OriginID],
        [DestinationTypeID],
        [DestinationID],
		[Cost],
		[DoNotMeetCommitment],
		[Commitment],
		[CustomerRate],
		[CustomerDiscount],
		[DrRate],
		[PartnerRate],
		[PartnerDiscount],
		[Profitability],
		[PickupCount],
		[DeliveryCount],
		[DockAdjustment],
		[Margin],
		[Density],
		[PickupCost],
		[DeliveryCost],
		[AccessorialsValue],
		[AccessorialsPercentage],
        [IsFlagged],
        [RequestSectionLaneSourceID],
        [Deficit],
        [EmbeddedCost],
        [ImpactPercentage]
	)
OUTPUT INSERTED.[RequestSectionLaneID]
INTO @RequestSectionLane
    (
	[RequestSectionLaneID]
    )
VALUES
(
    1,
	1,
	@RequestSectionID,
	0,
    0,
    0,
    @IsBetween,
	@OriginTypeID,
    @OriginID,
	@DestinationTypeID,
	@DestinationID,
    @Cost,
	0,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	NULL,
	NULL,
	NULL,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Flagged,
	@RequestSectionLaneSourceID,
	@Deficit,
	@EmbeddedCost,
	@ImpactPercentage
)

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT

SELECT R.RequestSectionLaneID AS request_section_lane_id
FROM RequestSectionLane R
WHERE R.RequestSectionID = @RequestSectionID
AND R.OriginID = @OriginID AND R.DestinationID = @DestinationID


IF (@ERROR1 <> 0)
	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

IF (@ROWCOUNT1 <> 1)

	BEGIN
	ROLLBACK TRAN
	IF (@ROWCOUNT1 <> 1)
		RAISERROR('%d Records Affected by Insert Procedure!', 16, 1, @ROWCOUNT1);

	RETURN 0
	END

COMMIT TRAN
RETURN 1
GO
