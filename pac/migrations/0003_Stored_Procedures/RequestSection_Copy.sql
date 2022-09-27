CREATE OR ALTER PROCEDURE [dbo].[RequestSection_Copy]
	@RequestSectionTableType_Pair     RequestSectionTableType_Pair READONLY,
	@RequestID BIGINT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL

AS

SET NOCOUNT ON;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Duplicating lanes.';

BEGIN TRAN

	DECLARE @RequestSectionLaneCost TABLE
	(
		[RequestSectionID] BIGINT NOT NULL,
		[Cost] NVARCHAR(MAX) NOT NULL
	)

	INSERT INTO @RequestSectionLaneCost
	(
		[RequestSectionID],
		[Cost]
	)
	SELECT RS.[SourceRequestSectionID],
		dbo.GetRequestSectionLaneDefaultCost(RS.[DestinationRequestSectionID])
	FROM @RequestSectionTableType_Pair RS 
	
	DECLARE @RequestSectionLaneTableType RequestSectionLaneTableType;

	INSERT INTO @RequestSectionLaneTableType
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
		[RequestSectionLaneID],
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
		[AccessorialsPercentage]
	)
	SELECT [IsActive],
		[IsInactiveViewable],
		RS.[DestinationRequestSectionID],
		0,
		0,
		0,
		[IsBetween],
        [OriginTypeID],
        [OriginID],
        [DestinationTypeID],
        [DestinationID],
		RSLC.Cost,
		[RequestSectionLaneID],
		0,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		NULL,
		NULL,
		NULL,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost
	FROM dbo.RequestSectionLane RSL
	INNER JOIN @RequestSectionTableType_Pair RS ON RSL.RequestSectionID = RS.[SourceRequestSectionID]
	INNER JOIN @RequestSectionLaneCost RSLC ON RS.[SourceRequestSectionID] = RSLC.RequestSectionID
	WHERE RSL.IsActive = 1 AND RSL.IsInactiveViewable = 1

COMMIT TRAN

