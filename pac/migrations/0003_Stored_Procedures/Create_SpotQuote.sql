CREATE OR ALTER PROCEDURE [dbo].[Create_SpotQuote]
	@UserID BIGINT,
    @SpotQuoteString NVARCHAR(max)
AS
SET ANSI_NULLS ON
SET QUOTED_IDENTIFIER ON
SET NOCOUNT ON;
BEGIN

    DECLARE @CurrencyID INT;
    DECLARE @ServiceLevel BIGINT;

    DECLARE @UsingStandardTariff BIT;
    DECLARE @SubjectToCube FLOAT;

    DECLARE @ShipmentString VARCHAR(1000);
    DECLARE @ShipmentOriginServicePoint BIGINT;
    DECLARE @ShipmentWeight FLOAT;
    DECLARE @ShipmentPercentUsage FLOAT;
    DECLARE @IsLiveLoadPickup BIT;
    DECLARE @ShipmentPickupsPerWeek INT;
    DECLARE @ShipmentPickupsPerMonth INT;
    DECLARE @ShipmentCommitment FLOAT;

    DECLARE @FreightString VARCHAR(1000);
    DECLARE @FreightDescription VARCHAR(100);
    DECLARE @FreightLength FLOAT;
    DECLARE @FreightWidth FLOAT;
    DECLARE @FreightHeight FLOAT;
    DECLARE @FreightWeight FLOAT;
    DECLARE @FreightPercentUsage FLOAT;

    DECLARE @SectionEquipmentType BIGINT;
    DECLARE @SectionSubServiceLevel BIGINT;
    DECLARE @SectionWeightBreakHeaderID BIGINT;
    DECLARE @SectionCommodityID BIGINT;

    DECLARE @IsBetween BIT;
    DECLARE @PickupCount INT;
    DECLARE @DeliveryCount INT;
    DECLARE @DestinationID BIGINT;
    DECLARE @DestinationTypeID INT;
    DECLARE @OriginID BIGINT;
    DECLARE @OriginTypeID INT;

    SELECT
        @CurrencyID = JSON_VALUE(@SpotQuoteString, '$.RequestInformation.CurrencyID'),
        @ServiceLevel = JSON_VALUE(@SpotQuoteString, '$.RequestInformation.ServiceLevel'),
        @UsingStandardTariff = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.UsingStandardTariff'),
        @SubjectToCube = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.SubjectToCube'),
        @ShipmentOriginServicePoint = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.Shipments[0].OriginServicePoint'),
        @ShipmentWeight = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.Shipments[0].Weight'),
        @ShipmentPercentUsage = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.Shipments[0].PercentUsage'),
        @IsLiveLoadPickup = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.Shipments[0].IsLiveLoadPickup'),
        @ShipmentPickupsPerWeek = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.Shipments[0].PickupsPerWeek'),
        @ShipmentPickupsPerMonth = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.Shipments[0].PickupsPerMonth'),
        @ShipmentCommitment = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.Shipments[0].Commitment'),
        @FreightDescription = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.FreightElements[0].Description'),
        @FreightLength = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.FreightElements[0].Length'),
        @FreightWidth = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.FreightElements[0].Width'),
        @FreightHeight = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.FreightElements[0].Height'),
        @FreightWeight = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.FreightElements[0].Weight'),
        @FreightPercentUsage = JSON_VALUE(@SpotQuoteString, '$.RequestProfile.FreightElements[0].PercentUsage'),
        @SectionEquipmentType = JSON_VALUE(@SpotQuoteString, '$.RequestSection.EquipmentType'),
        @SectionSubServiceLevel = JSON_VALUE(@SpotQuoteString, '$.RequestSection.SubServiceLevel'),
        @SectionWeightBreakHeaderID = JSON_VALUE(@SpotQuoteString, '$.RequestSection.WeightBreakHeaderID'),
        @SectionCommodityID = JSON_VALUE(@SpotQuoteString, '$.RequestSection.CommodityID'),
        @IsBetween = JSON_VALUE(@SpotQuoteString, '$.RequestSectionLane.IsBetween'),
        @PickupCount = JSON_VALUE(@SpotQuoteString, '$.RequestSectionLane.PickupCount'),
        @DeliveryCount = JSON_VALUE(@SpotQuoteString, '$.RequestSectionLane.DeliveryCount'),
        @DestinationID = JSON_VALUE(@SpotQuoteString, '$.RequestSectionLane.DestinationID'),
        @DestinationTypeID = JSON_VALUE(@SpotQuoteString, '$.RequestSectionLane.DestinationTypeID'),
        @OriginID = JSON_VALUE(@SpotQuoteString, '$.RequestSectionLane.OriginID'),
        @OriginTypeID = JSON_VALUE(@SpotQuoteString, '$.RequestSectionLane.OriginTypeID'),

        @ShipmentString = JSON_QUERY(@SpotQuoteString, '$.RequestProfile.Shipments'),
        @FreightString = JSON_QUERY(@SpotQuoteString, '$.RequestProfile.FreightElements')
     FROM OPENJSON(@SpotQuoteString, '$') sq;

    -- validate IDs
    DECLARE @ValidIds VARCHAR(20);
    SELECT @ValidIds = (CASE WHEN checks.found = 0 THEN 'Fail' ELSE 'Success' END) FROM
    (SELECT count(*) found
    WHERE EXISTS (SELECT * from dbo.Currency WHERE CurrencyID = @CurrencyID)
        AND EXISTS (SELECT * from dbo.ServiceLevel WHERE ServiceLevelID = @ServiceLevel)
        --Commenting since ServicePointID are currently Null in V_LocationTree
        --AND EXISTS (SELECT * from dbo.ServicePoint WHERE ServicePointID = @ShipmentOriginServicePoint)
        AND EXISTS (SELECT * from dbo.EquipmentType WHERE EquipmentTypeID = @SectionEquipmentType)
        AND EXISTS (SELECT * from dbo.SubServiceLevel WHERE SubServiceLevelID = @SectionSubServiceLevel
            AND ServiceLevelID = @ServiceLevel)
        AND EXISTS (SELECT * from dbo.WeightBreakHeader WHERE WeightBreakHeaderID = @SectionWeightBreakHeaderID
            AND ServiceLevelID = @ServiceLevel)
        AND EXISTS (SELECT * from dbo.Commodity WHERE CommodityID = @SectionCommodityID)
        AND EXISTS (SELECT * from dbo.V_LocationTree WHERE PointTypeID = @DestinationTypeID AND ID = @DestinationID)
        AND EXISTS (SELECT * from dbo.V_LocationTree WHERE PointTypeID = @OriginTypeID AND ID = @OriginID)
    ) checks;

    IF @ValidIds = 'Fail'
    BEGIN
        SELECT 'Invalid IDs were provided' as ErrorMessage;
        RETURN;
    END

    DECLARE @NewRequestID BIGINT;
    DECLARE @NewRequestCode VARCHAR(50);
    DECLARE @NewRequestProfileID BIGINT;
    DECLARE @NewRequestInfoID BIGINT;
    DECLARE @NewRequestSectionID BIGINT;
    DECLARE @NewRequestSectionLaneID BIGINT;
    DECLARE @SpotQuoteCustomer BIGINT;
    DECLARE @RequestTypeID BIGINT;

    SELECT top(1) @SpotQuoteCustomer = c.CustomerID FROM dbo.Customer c;
    SELECT @RequestTypeID = RequestTypeID FROM dbo.RequestType where RequestTypeName = 'Commitment';
    -- SpeedsheetName
    BEGIN TRANSACTION
        BEGIN TRY
            -- create the Request
            INSERT INTO dbo.Request (InitiatedOn,InitiatedBy, SubmittedOn,SubmittedBy,IsValidData,IsReview,UniType,LanguageID,RequestOwner,
                RequestSourceID, IsActive, IsInactiveViewable, RequestStatusTypeID, CurrentEditorID, RequestMajorVersion, NewLanesOnly)
            VALUES
            (CURRENT_TIMESTAMP,@UserID,null, @UserID,1,0,'Spot Quote',1,@UserID,null, 1, 1, 14, @UserID,1,0);
            SELECT @NewRequestID = SCOPE_IDENTITY();
            SELECT @NewRequestCode =  CONVERT(VARCHAR, 200000000 + RequestID) from dbo.Request where RequestID = @NewRequestID;
            UPDATE dbo.Request SET RequestCode = @NewRequestCode WHERE RequestID = @NewRequestID;

            -- create the RequestInformation
            INSERT INTO dbo.RequestInformation (RequestID,IsValidData,IsNewBusiness,
                CurrencyID,CustomerID,LanguageID,RequestTypeID,EffectiveDate,ExpiryDate,IsActive, IsInactiveViewable)
            VALUES
            (@NewRequestID,1,1,
                @CurrencyID, @SpotQuoteCustomer,1, @RequestTypeID,CURRENT_TIMESTAMP,DATEADD(DAY, 60, CURRENT_TIMESTAMP),1, 1);
            SELECT @NewRequestInfoID = SCOPE_IDENTITY();

            -- create the RequestProfile
            INSERT INTO dbo.RequestProfile (RequestID,IsActive,IsInactiveViewable,IsValidData,UsingStandardTariff,IsClassDensity,SubjectToCube,FreightElements,Shipments)
            VALUES
            (@NewRequestID,1,1,1,@UsingStandardTariff,1,@SubjectToCube,@FreightString,@ShipmentString);
            SELECT @NewRequestProfileID = SCOPE_IDENTITY();

            -- create the RequestSection
            DECLARE @Levels VARCHAR(1000);
            DECLARE @HasMax BIT,@HasMin BIT, @AsRating BIT, @BaseRate BIT;
            DECLARE @MaximumValue INT, @UnitFactor INT;
            SELECT @Levels = Levels, @HasMax = HasMax , @HasMin = HasMin , @UnitFactor = UnitFactor,
                @AsRating = AsRating , @BaseRate = BaseRate , @MaximumValue = MaximumValue
            FROM dbo.WeightBreakHeader WHERE WeightBreakHeaderID = @SectionWeightBreakHeaderID; -- copy value from WeightBreak

            INSERT INTO dbo.RequestSection (IsActive,IsInactiveViewable,SectionName,WeightBreak,IsDensityPricing ,EquipmentTypeID ,RequestID ,CommodityID ,
                SubServiceLevelID ,WeightBreakHeaderID,HasMax ,HasMin ,UnitFactor ,AsRating ,BaseRate ,MaximumValue)
            VALUES
            (1,1,'Spot Quote Section',@Levels,1 ,@SectionEquipmentType ,@NewRequestID ,@SectionCommodityID ,
                @SectionSubServiceLevel ,@SectionWeightBreakHeaderID, @HasMax ,@HasMin ,@UnitFactor ,@AsRating ,@BaseRate ,@MaximumValue);
            SELECT @NewRequestSectionID = SCOPE_IDENTITY();

            -- create the RequestSectionLane
            DECLARE @EmptyCost VARCHAR(10) = '{}';
            INSERT INTO dbo.RequestSectionLane (IsActive ,IsInactiveViewable ,RequestSectionID ,IsPublished ,IsEdited ,IsDuplicate ,IsBetween,
                DestinationID ,DestinationTypeID ,OriginID ,OriginTypeID, PickupCount ,DeliveryCount,
                DoNotMeetCommitment, Cost,Commitment,CustomerRate ,CustomerDiscount ,DrRate,PartnerRate ,PartnerDiscount ,Profitability,Margin ,
                Density ,PickupCost ,DeliveryCost ,AccessorialsValue ,AccessorialsPercentage )
            VALUES
            (1 ,1 ,@NewRequestSectionID,0 ,0 ,0 ,@IsBetween,
                @DestinationID ,@DestinationTypeID ,@OriginID ,@OriginTypeID, @PickupCount ,@DeliveryCount,
                0,@EmptyCost,@EmptyCost,@EmptyCost ,@EmptyCost ,@EmptyCost,@EmptyCost ,@EmptyCost ,@EmptyCost,@EmptyCost ,
                @EmptyCost ,@EmptyCost ,@EmptyCost ,@EmptyCost ,@EmptyCost );
            SELECT @NewRequestSectionLaneID = SCOPE_IDENTITY();

            -- Add Audit records
            EXEC dbo.[Audit_Record] @TableName = 'RequestInformation', @PrimaryKeyValue = @NewRequestInfoID, @UpdatedBy = 'Spot Quote Creation';
            EXEC dbo.[Audit_Record] @TableName = 'RequestProfile', @PrimaryKeyValue = @NewRequestProfileID, @UpdatedBy = 'Spot Quote Creation';
            EXEC dbo.[Audit_Record] @TableName = 'RequestSection', @PrimaryKeyValue = @NewRequestSectionID, @UpdatedBy = 'Spot Quote Creation';
            EXEC dbo.[Audit_Record] @TableName = 'RequestSectionLane', @PrimaryKeyValue = @NewRequestSectionLaneID, @UpdatedBy = 'Spot Quote Creation';
            EXEC dbo.[Audit_Record] @TableName = 'Request', @PrimaryKeyValue = @NewRequestID, @UpdatedBy = 'Spot Quote Creation';
            COMMIT; -- Commit changes if all were successful, then return the new RequestID
        END TRY
        BEGIN CATCH
            SELECT 'Unable to create records', ERROR_MESSAGE() AS ErrorMessage;
            ROLLBACK;
            RETURN;
        END CATCH;
    SELECT r.RequestID, rsl.RequestSectionLaneID from dbo.Request r
    INNER JOIN dbo.RequestSection rs ON rs.RequestID = r.RequestID
    INNER JOIN dbo.RequestSectionLane rsl ON rsl.RequestSectionID = rs.RequestSectionID
    WHERE r.RequestID = @NewRequestID;
END
