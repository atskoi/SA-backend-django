GET_ACCOUNT_HISTORY = """
DECLARE @AccountID BIGINT;
SELECT @AccountID = C.AccountID
FROM dbo.Request R
INNER JOIN dbo.RequestInformation RI ON R.RequestID = RI.RequestID
INNER JOIN dbo.Customer C ON RI.CustomerID = C.CustomerID
WHERE R.RequestID = {0}

SELECT CAST(
(SELECT *
FROM
(
	SELECT R.RequestID AS request_id,
		R.RequestCode AS request_code,
		C.AccountID as account_id,
		CASE WHEN C.AccountID IS NULL THEN 'New' ELSE 'Expanded' END AS business_type_name,
		ISNULL(RS.SalesRepresentativeID, '') AS sales_representative_id,
		ISNULL(SR.UserName, '') AS sales_representative_name,
		ISNULL(RS.PricingAnalystID, '') AS pricing_analyst_id,
		ISNULL(PA.UserName, '') AS pricing_analyst_name,
		ISNULL(R.SubmittedOn, '') AS date_submitted,
		ISNULL(T.PublishedOn, '') AS date_published,
		ISNULL(T.ExpiresOn, '') AS expiration_date,
		ISNULL(T.DocumentUrl, '') AS document_url
	FROM dbo.Account A
		RIGHT JOIN dbo.Customer C ON A.AccountID = C.AccountID
		INNER JOIN dbo.RequestInformation RI ON C.CustomerID = RI.CustomerID
		INNER JOIN dbo.Request R ON RI.RequestID = R.RequestID
		LEFT JOIN dbo.Tariff T ON R.RequestID = T.RequestID
		LEFT JOIN dbo.RequestStatus RS ON R.RequestID = RS.RequestID
		LEFT JOIN dbo.[User] SR ON RS.SalesRepresentativeID = SR.UserID
		LEFT JOIN dbo.[User] PA ON RS.PricingAnalystID = PA.UserID
	WHERE A.AccountID = @AccountID) AS Q
	FOR JSON AUTO)
	AS VARCHAR(MAX))
"""

GET_ACCOUNT_ID = """
DECLARE @RequestID BIGINT = {0};

SELECT C.AccountID, c.ServiceLevelID
FROM dbo.Request R
INNER JOIN dbo.RequestInformation RI ON R.RequestID = RI.RequestID
INNER JOIN dbo.Customer C ON RI.CustomerID = C.CustomerID
WHERE R.RequestID = {0}
"""

GET_TARIFF_HISTORY = """
DECLARE @CustomerID BIGINT;
SELECT @CustomerID = C.CustomerID
FROM dbo.Request R
INNER JOIN dbo.RequestInformation RI ON R.RequestID = RI.RequestID
INNER JOIN dbo.Customer C ON RI.CustomerID = C.CustomerID
WHERE R.RequestID = {0}

SELECT CAST(
(SELECT *
FROM
(
	SELECT R.RequestID AS request_id,
		R.RequestCode AS request_code,
		CASE WHEN C.AccountID IS NULL THEN 'New' ELSE 'Expanded' END AS business_type_name,
		RH.VersionNum AS version_num,
		RH.UpdatedOn AS version_saved_on,
		RH.UpdatedBy AS saved_by,
		RH.Comments AS comments
	FROM Customer C 
		INNER JOIN dbo.RequestInformation RI ON C.CustomerID = RI.CustomerID
		INNER JOIN dbo.Request R ON RI.RequestID = R.RequestID
		INNER JOIN dbo.Request_History RH ON R.RequestID = RH.RequestID AND RH.IsLatestVersion = 1
	WHERE C.CustomerID = @CustomerID) AS Q
	FOR JSON AUTO)
	AS VARCHAR(MAX))
"""

GET_REQUEST_LANE_LOCATION_TREE = """
DECLARE @RequestSectionID BIGINT = {0};
DECLARE @OrigPointTypeName NVARCHAR(50) = '{1}';
DECLARE @OrigPointID BIGINT = {2};
DECLARE @DestPointTypeName NVARCHAR(50) = '{3}';
DECLARE @DestPointID BIGINT = {4};
DECLARE @LaneStatusName NVARCHAR(50) = '{5}';

With RequestSectionLanes AS 
(SELECT RSL.*
FROM dbo.RequestSectionLane{6} RSL
WHERE RSL.RequestSectionID = @RequestSectionID AND RSL.IsActive = 1 AND RSL.IsInactiveViewable = 1
AND	( (@LaneStatusName = 'None') OR (@LaneStatusName = 'New' AND [IsPublished] = 0) OR (@LaneStatusName = 'Changed' AND [IsEdited] = 1) OR (@LaneStatusName = 'Duplicated' AND [IsDuplicate] = 1) OR (@LaneStatusName = 'DoNotMeetCommitment' AND [DoNotMeetCommitment] = 1))
	AND ( (@OrigPointTypeName = 'None') OR
		(@OrigPointTypeName = 'Country' AND OriginCountryID = @OrigPointID) OR (@OrigPointTypeName = 'Region' AND OriginRegionID = @OrigPointID)
		OR
		(@OrigPointTypeName = 'Province' AND OriginProvinceID = @OrigPointID) OR (@OrigPointTypeName = 'Terminal' AND OriginTerminalID = @OrigPointID)
		OR 
		(@OrigPointTypeName = 'Basing Point' AND OriginBasingPointID = @OrigPointID) OR (@OrigPointTypeName = 'Service Point' AND OriginServicePointID = @OrigPointID)
		OR
		(@OrigPointTypeName = 'Postal Code' AND OriginPostalCodeID = @OrigPointID) OR (@OrigPointTypeName = 'Point Type' AND OriginPointTypeID = @OrigPointID)
		)
	AND ( (@DestPointTypeName = 'None') OR
		(@DestPointTypeName = 'Country' AND DestinationCountryID = @DestPointID) OR (@DestPointTypeName = 'Region' AND DestinationRegionID = @DestPointID)
		OR
		(@DestPointTypeName = 'Province' AND DestinationProvinceID = @DestPointID) OR (@DestPointTypeName = 'Terminal' AND DestinationTerminalID = @DestPointID)
		OR 
		(@DestPointTypeName = 'Basing Point' AND DestinationBasingPointID = @DestPointID) OR (@DestPointTypeName = 'Service Point' AND DestinationServicePointID = @DestPointID)
		OR
		(@DestPointTypeName = 'Postal Code' AND DestinationPostalCodeID = @DestPointID) OR (@DestPointTypeName = 'Point Type' AND DestinationPointTypeID = @DestPointID)
		)
),
O_PC AS 
(SELECT DISTINCT OriginPostalCodeID AS postal_code_id, OriginPostalCodeName AS postal_code_name
FROM RequestSectionLanes
WHERE OriginPostalCodeID IS NOT NULL),
D_PC AS 
(SELECT DISTINCT DestinationPostalCodeID AS postal_code_id, DestinationPostalCodeName AS postal_code_name
FROM RequestSectionLanes
WHERE DestinationPostalCodeID IS NOT NULL),
O_SP AS 
(SELECT DISTINCT OriginServicePointID AS service_point_id, OriginServicePointName AS service_point_name
FROM RequestSectionLanes
WHERE OriginServicePointID IS NOT NULL),
D_SP AS 
(SELECT DISTINCT DestinationServicePointID AS service_point_id, DestinationServicePointName AS service_point_name
FROM RequestSectionLanes
WHERE DestinationServicePointID IS NOT NULL),
O_T AS 
(SELECT DISTINCT OriginTerminalID AS terminal_id, OriginTerminalCode AS terminal_code
FROM RequestSectionLanes
WHERE OriginTerminalID IS NOT NULL),
D_T AS 
(SELECT DISTINCT DestinationTerminalID AS terminal_id, DestinationTerminalCode AS terminal_code
FROM RequestSectionLanes 
WHERE DestinationTerminalID IS NOT NULL),
O_BP AS 
(SELECT DISTINCT OriginBasingPointID AS basing_point_id, OriginBasingPointName AS basing_point_name
FROM RequestSectionLanes
WHERE OriginBasingPointID IS NOT NULL),
D_BP AS 
(SELECT DISTINCT DestinationBasingPointID AS basing_point_id, DestinationBasingPointName AS basing_point_name
FROM RequestSectionLanes
WHERE DestinationBasingPointID IS NOT NULL),
O_P AS 
(SELECT DISTINCT OriginProvinceID AS province_id, OriginProvinceCode AS province_code
FROM RequestSectionLanes
WHERE OriginProvinceID IS NOT NULL),
D_P AS 
(SELECT DISTINCT DestinationProvinceID AS province_id, DestinationProvinceCode AS province_code
FROM RequestSectionLanes
WHERE DestinationProvinceID IS NOT NULL),
O_R AS 
(SELECT DISTINCT OriginRegionID AS region_id, OriginRegionCode AS region_code
FROM RequestSectionLanes
WHERE OriginRegionID IS NOT NULL),
D_R AS 
(SELECT DISTINCT DestinationRegionID AS region_id, DestinationRegionCode AS region_code
FROM RequestSectionLanes
WHERE DestinationRegionID IS NOT NULL),
O_C AS 
(SELECT DISTINCT OriginCountryID AS country_id, OriginCountryCode AS country_code
FROM RequestSectionLanes
WHERE OriginCountryID IS NOT NULL),
D_C AS 
(SELECT DISTINCT DestinationCountryID AS country_id, DestinationCountryCode AS country_code
FROM RequestSectionLanes
WHERE DestinationCountryID IS NOT NULL),
O_Z AS 
(SELECT DISTINCT OriginZoneID AS zone_id, OriginZoneName AS zone_name
FROM RequestSectionLanes
WHERE OriginZoneID IS NOT NULL),
D_Z AS 
(SELECT DISTINCT DestinationZoneID AS zone_id, DestinationZoneName AS zone_name
FROM RequestSectionLanes
WHERE DestinationZoneID IS NOT NULL),
O_PT AS 
(SELECT DISTINCT OriginPointTypeID AS point_type_id, OriginPointTypeName AS point_type_name
FROM RequestSectionLanes
WHERE OriginPointTypeID IS NOT NULL),
D_PT AS 
(SELECT DISTINCT DestinationPointTypeID AS point_type_id, DestinationPointTypeName AS point_type_name
FROM RequestSectionLanes
WHERE DestinationPointTypeID IS NOT NULL),
Origin AS 
(SELECT 
	(SELECT * FROM O_PT FOR JSON AUTO) AS point_types,
	(SELECT * FROM O_Z FOR JSON AUTO) AS zones,
	(SELECT * FROM O_C FOR JSON AUTO) AS countries,
	(SELECT * FROM O_R FOR JSON AUTO) AS regions,
	(SELECT * FROM O_P FOR JSON AUTO) AS provinces,
	(SELECT * FROM O_BP FOR JSON AUTO) AS basing_points,
	(SELECT * FROM O_T FOR JSON AUTO) AS terminals,
	(SELECT * FROM O_SP FOR JSON AUTO) AS service_points,
	(SELECT * FROM O_PC FOR JSON AUTO) AS postal_codes
),
Destination AS 
(SELECT
	(SELECT * FROM D_PT FOR JSON AUTO) AS point_types,
	(SELECT * FROM D_Z FOR JSON AUTO) AS zones,
	(SELECT * FROM D_C FOR JSON AUTO) AS countries,
	(SELECT * FROM D_R FOR JSON AUTO) AS regions,
	(SELECT * FROM D_P FOR JSON AUTO) AS provinces,
	(SELECT * FROM D_BP FOR JSON AUTO) AS basing_points,
	(SELECT * FROM D_T FOR JSON AUTO) AS terminals,
	(SELECT * FROM D_SP FOR JSON AUTO) AS service_points,
	(SELECT * FROM D_PC FOR JSON AUTO) AS postal_codes
)

SELECT CAST(
(SELECT *
FROM
(
SELECT (SELECT * FROM Origin FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS orig, (SELECT * FROM Destination FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS dest
) AS Q
	FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER)
	AS VARCHAR(MAX))
"""

SEARCH_REQUEST_SECTION_LANE_POINTS = """ 
SELECT CAST(
(SELECT *
FROM
(
SELECT *
FROM dbo.SearchRequestSectionLanePoints('{0}', {1}, '{2}', '{3}')) AS Q
	FOR JSON AUTO)
	AS VARCHAR(MAX)) 
"""

SEARCH_ORIGIN_POSTAL_CODE = """ 
DECLARE @PostalCodeID BIGINT = (SELECT OriginID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND OriginTypeID = 7);

IF @PostalCodeID IS NOT NULL
BEGIN
	SELECT CAST((SELECT * FROM (
	SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
	FROM dbo.PostalCode PC
	WHERE PC.PostalCodeID = @PostalCodeID AND PC.PostalCodeName LIKE '{1}%'
	) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
END
ELSE
BEGIN
	DECLARE @ServicePointID BIGINT = (SELECT OriginID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND OriginTypeID = 6);
	IF @ServicePointID IS NOT NULL
	BEGIN
		SELECT CAST((SELECT * FROM (
		SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
		FROM dbo.PostalCode PC
		INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
        INNER JOIN dbo.Region r ON r.RegionID = p.RegionID
        INNER JOIN dbo.Terminal t ON t.RegionID = r.RegionID
        INNER JOIN dbo.ServicePoint sp ON sp.TerminalID = t.TerminalID
		WHERE SP.ServicePointID = @ServicePointID AND PC.PostalCodeName LIKE '{1}%'
		) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
	END
	ELSE
	BEGIN
		DECLARE @BasingPointID BIGINT = (SELECT OriginID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0}	AND OriginTypeID = 5);
		IF @BasingPointID IS NOT NULL
		BEGIN
			SELECT CAST((SELECT * FROM (
			SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
			FROM dbo.PostalCode PC
            INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
            INNER JOIN dbo.Region r ON r.RegionID = p.RegionID
            INNER JOIN dbo.Terminal t ON t.RegionID = r.RegionID
			INNER JOIN dbo.BasingPoint BP ON bp.TerminalID = t.TerminalID
			WHERE BP.BasingPointID = @BasingPointID AND PC.PostalCodeName LIKE '{1}%'
			) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
		END
		ELSE
		BEGIN
			DECLARE @TerminalID BIGINT = (SELECT OriginID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND OriginTypeID = 4);
			IF @TerminalID IS NOT NULL
			BEGIN
				SELECT CAST((SELECT * FROM (
				SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
				FROM dbo.PostalCode PC
                INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
                INNER JOIN dbo.Region r ON r.RegionID = p.RegionID
                INNER JOIN dbo.Terminal t ON t.RegionID = r.RegionID
				WHERE t.TerminalID = @TerminalID AND PC.PostalCodeName LIKE '{1}%'
				) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
			END
			ELSE
			BEGIN
				DECLARE @ProvinceID BIGINT = (SELECT OriginID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND OriginTypeID = 3);
				IF @ProvinceID IS NOT NULL
				BEGIN
					SELECT CAST((SELECT * FROM (
					SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
					FROM dbo.PostalCode PC
                    INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
					WHERE P.ProvinceID = @ProvinceID AND PC.PostalCodeName LIKE '{1}%'
					) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
				END
				ELSE
				BEGIN
					DECLARE @RegionID BIGINT = (SELECT OriginID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND OriginTypeID = 2);
					IF @RegionID IS NOT NULL
					BEGIN
						SELECT CAST((SELECT * FROM (
						SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
						FROM dbo.PostalCode PC
                        INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
                        INNER JOIN dbo.Region r ON r.RegionID = p.RegionID
						WHERE R.RegionID = @RegionID AND PC.PostalCodeName LIKE '{1}%'
						) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
					END
					ELSE
					BEGIN
						DECLARE @CountryID BIGINT = (SELECT OriginID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND OriginTypeID = 1);

						SELECT CAST((SELECT * FROM (
						SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
						FROM dbo.PostalCode PC
                        INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
                        INNER JOIN dbo.Region r ON r.RegionID = p.RegionID
						LEFT JOIN dbo.Country C ON R.CountryID = C.CountryID
						WHERE C.CountryID = @CountryID AND PC.PostalCodeName LIKE '{1}%'
						) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
					END
				END
			END
		END
	END
END
"""

SEARCH_DESTINATION_POSTAL_CODE = """
DECLARE @PostalCodeID BIGINT = (SELECT DestinationID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND DestinationTypeID = 7);

IF @PostalCodeID IS NOT NULL
BEGIN
	SELECT CAST((SELECT * FROM (
	SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
	FROM dbo.PostalCode PC
	WHERE PC.PostalCodeID = @PostalCodeID AND PC.PostalCodeName LIKE '{1}%'
	) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
END
ELSE
BEGIN
	DECLARE @ServicePointID BIGINT = (SELECT DestinationID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND DestinationTypeID = 6);
	IF @ServicePointID IS NOT NULL
	BEGIN
		SELECT CAST((SELECT * FROM (
		SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
		FROM dbo.PostalCode PC
		INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
        INNER JOIN dbo.Region r ON r.RegionID = p.RegionID
        INNER JOIN dbo.Terminal t ON t.RegionID = r.RegionID
        INNER JOIN dbo.ServicePoint sp ON sp.TerminalID = t.TerminalID
		WHERE SP.ServicePointID = @ServicePointID AND PC.PostalCodeName LIKE '{1}%'
		) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
	END
	ELSE
	BEGIN
		DECLARE @BasingPointID BIGINT = (SELECT DestinationID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND DestinationTypeID = 5);
		IF @BasingPointID IS NOT NULL
		BEGIN
			SELECT CAST((SELECT * FROM (
			SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
			FROM dbo.PostalCode PC
            INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
            INNER JOIN dbo.Region r ON r.RegionID = p.RegionID
            INNER JOIN dbo.Terminal t ON t.RegionID = r.RegionID
			INNER JOIN dbo.BasingPoint BP ON bp.TerminalID = t.TerminalID
			WHERE BP.BasingPointID = @BasingPointID AND PC.PostalCodeName LIKE '{1}%'
			) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
		END
		ELSE
		BEGIN
			DECLARE @TerminalID BIGINT = (SELECT DestinationID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND DestinationTypeID = 4);
			IF @TerminalID IS NOT NULL
			BEGIN
				SELECT CAST((SELECT * FROM (
				SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
				FROM dbo.PostalCode PC
                INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
                INNER JOIN dbo.Region r ON r.RegionID = p.RegionID
                INNER JOIN dbo.Terminal t ON t.RegionID = r.RegionID
				WHERE t.TerminalID = @TerminalID AND PC.PostalCodeName LIKE '{1}%'
				) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
			END
			ELSE
			BEGIN
				DECLARE @ProvinceID BIGINT = (SELECT DestinationID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND DestinationTypeID = 3);
				IF @ProvinceID IS NOT NULL
				BEGIN
					SELECT CAST((SELECT * FROM (
					SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
					FROM dbo.PostalCode PC
                    INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
					WHERE P.ProvinceID = @ProvinceID AND PC.PostalCodeName LIKE '{1}%'
					) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
				END
				ELSE
				BEGIN
					DECLARE @RegionID BIGINT = (SELECT DestinationID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} AND DestinationTypeID = 2);
					IF @RegionID IS NOT NULL
					BEGIN
						SELECT CAST((SELECT * FROM (
						SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
						FROM dbo.PostalCode PC
                        INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
                        INNER JOIN dbo.Region r ON r.RegionID = p.RegionID
						WHERE R.RegionID = @RegionID AND PC.PostalCodeName LIKE '{1}%'
						) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
					END
					ELSE
					BEGIN
						DECLARE @CountryID BIGINT = (SELECT DestinationID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0} and DestinationTypeID = 1);

						SELECT CAST((SELECT * FROM (
						SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
						FROM dbo.PostalCode PC
                        INNER JOIN dbo.Province p ON p.ProvinceID = pc.ProvinceID
                        INNER JOIN dbo.Region r ON r.RegionID = p.RegionID
						LEFT JOIN dbo.Country C ON R.CountryID = C.CountryID
						WHERE C.CountryID = @CountryID AND PC.PostalCodeName LIKE '{1}%'
						) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
					END
				END
			END
		END
	END
END
"""

GET_PRICING_POINTS = """
	SELECT RequestSectionLanePricingPointID AS request_section_lane_pricing_point_id,
	RequestSectionLaneID,
	OriginPostalCodeID AS origin_postal_code_id,
	OriginPostalCodeName AS origin_postal_code_name,
	DestinationPostalCodeID AS destination_postal_code_id,
	DestinationPostalCodeName AS destination_postal_code_name,
	DrRate AS dr_rate,
	FakRate AS fak_rate,
	Profitability AS profitability,
	Cost AS cost,
	SplitsAll AS splits_all,
	SplitsAllUsagePercentage AS splits_all_usage_percentage,
	PickupCount AS pickup_count,
	DeliveryCount AS delivery_count,
	DockAdjustment AS dock_adjustment,
	Margin AS margin,
	Density AS density,
	PickupCost AS pickup_cost,
	DeliveryCost AS delivery_cost,
	AccessorialsValue AS accessorials_value,
	AccessorialsPercentage AS accessorials_percentage,
	IsActive AS is_active,
	IsInactiveViewable AS is_inactive_viewable,
	CostOverrideAccessorialsPercentage  AS cost_override_accessorials_percentage,
    CostOverrideAccessorialsValue  AS  cost_override_accessorials_value,
    CostOverrideDeliveryCost  AS cost_override_delivery_cost,
    CostOverrideDeliveryCount  AS cost_override_delivery_count,
    CostOverrideDensity  AS cost_override_density,
    CostOverrideDockAdjustment  AS cost_override_dock_adjustment,
    CostOverrideMargin  AS cost_override_margin,
    CostOverridePickupCost  AS cost_override_pickup_cost,
    CostOverridePickupCount  AS cost_override_pickup_count,
	PricingRates AS pricing_rates,
	WorkflowErrors AS workflow_errors,
	IsFlagged AS is_flagged
FROM dbo.RequestSectionLanePricingPoint RSLPP
WHERE RSLPP.RequestSectionLaneID = {0}
AND RSLPP.IsActive = 1 AND RSLPP.IsInactiveViewable = 1
"""

UPDATE_PRICING_POINTS_COST_OVERRIDE = """
UPDATE RequestSectionLanePricingPoint
SET CostOverrideAccessorialsPercentage ='{0}',
    CostOverrideAccessorialsValue ='{1}',
    CostOverrideDeliveryCost='{2}',
    CostOverrideDeliveryCount={3},
    CostOverrideDensity='{4}',
    CostOverrideDockAdjustment={5},
    CostOverrideMargin = '{6}',
    CostOverridePickupCost = '{7}',
    CostOverridePickupCount ='{8}'

WHERE RequestSectionLanePricingPointID IN ({9})
"""

GET_PRICING_POINTS_HISTORY = """
 SELECT CAST((SELECT * FROM (
	SELECT RSLPPH.RequestSectionLanePricingPointID AS request_section_lane_pricing_point_id,
	RSL.RequestSectionLaneID AS request_section_lane_id,
	RSLPP.OriginPostalCodeID AS origin_postal_code_id,
	RSLPPH.OriginPostalCodeName AS origin_postal_code_name,
	RSLPP.DestinationPostalCodeID AS destination_postal_code_id,
	RSLPPH.DestinationPostalCodeName AS destination_postal_code_name,
	RSLPPH.DrRate AS dr_rate,
	RSLPPH.FakRate AS fak_rate,
	RSLPPH.Profitability AS profitability,
	RSLPPH.Cost AS cost,
	RSLPPH.SplitsAll AS splits_all,
	RSLPPH.SplitsAllUsagePercentage AS splits_all_usage_percentage,
	RSLPPH.PickupCount AS pickup_count,
	RSLPPH.DeliveryCount AS delivery_count,
	RSLPPH.DockAdjustment AS dock_adjustment,
	RSLPPH.Margin AS margin,
	RSLPPH.Density AS density,
	RSLPPH.PickupCost AS pickup_cost,
	RSLPPH.DeliveryCost AS delivery_cost,
	RSLPPH.AccessorialsValue AS accessorials_value,
	RSLPPH.AccessorialsPercentage AS accessorials_percentage,
	RSLPPH.IsActive AS is_active,
	RSLPPH.IsInactiveViewable AS is_inactive_viewable,
	RSLPPH.CostOverrideAccessorialsPercentage  AS cost_override_accessorials_percentage,
    RSLPPH.CostOverrideAccessorialsValue  AS  cost_override_accessorials_value,
    RSLPPH.CostOverrideDeliveryCost  AS cost_override_delivery_cost,
    RSLPPH.CostOverrideDeliveryCount  AS cost_override_delivery_count,
    RSLPPH.CostOverrideDensity  AS cost_override_density,
    RSLPPH.CostOverrideDockAdjustment  AS cost_override_dock_adjustment,
    RSLPPH.CostOverrideMargin  AS cost_override_margin,
    RSLPPH.CostOverridePickupCost  AS cost_override_pickup_cost,
    RSLPPH.CostOverridePickupCount  AS cost_override_pickup_count,
	RSLPPH.PricingRates AS pricing_rates,
	RSLPPH.WorkflowErrors AS workflow_errors
FROM dbo.RequestSectionLanePricingPoint_History RSLPPH
INNER JOIN dbo.RequestSectionLanePricingPoint RSLPP ON RSLPPH.RequestSectionLanePricingPointID = RSLPP.RequestSectionLanePricingPointID
INNER JOIN dbo.RequestSectionLane_History RSL ON RSLPPH.RequestSectionLaneVersionID = RSL.RequestSectionLaneVersionID
INNER JOIN dbo.RequestSection_History RS ON RSL.RequestSectionVersionID = RS.RequestSectionVersionID
INNER JOIN dbo.RequestLane_History RL ON RS.RequestLaneVersionID = RL.RequestLaneVersionID
INNER JOIN dbo.Request_History R ON RL.RequestLaneVersionID = R.RequestLaneVersionID
WHERE RSL.RequestSectionLaneID = {0}
AND RSLPPH.IsActive = 1 AND RSLPPH.IsInactiveViewable = 1 AND R.VersionNum = {1}
) AS Q FOR JSON AUTO, INCLUDE_NULL_VALUES) AS VARCHAR(MAX))
"""

GET_PRICING_POINTS_Staging = """
 SELECT CAST((SELECT * FROM (
	SELECT RequestSectionLanePricingPointID AS request_section_lane_pricing_point_id,
	RequestSectionLaneID AS request_section_lane_id,
	OriginPostalCodeID AS origin_postal_code_id,
	OriginPostalCodeName AS origin_postal_code_name,
	DestinationPostalCodeID AS destination_postal_code_id,
	DestinationPostalCodeName AS destination_postal_code_name,
	DrRate AS dr_rate,
	NewDrRate AS new_dr_rate,
	FakRate AS fak_rate,
	NewFakRate AS new_fak_rate,
	Profitability AS profitability,
	Cost AS cost,
	NewProfitability AS new_profitability,
	SplitsAll AS splits_all,
	NewSplitsAll AS new_splits_all,
	SplitsAllUsagePercentage AS splits_all_usage_percentage,
	NewSplitsAllUsagePercentage AS new_splits_all_usage_percentage,
	PickupCount AS pickup_count,
	NewPickupCount AS new_pickup_count,
	DeliveryCount AS delivery_count,
	NewDeliveryCount AS new_delivery_count,
	DockAdjustment AS dock_adjustment,
	NewDockAdjustment AS new_dock_adjustment,
	Margin AS margin,
	NewMargin AS new_margin,
	Density AS density,
	NewDensity AS new_density,
	PickupCost AS pickup_cost,
	NewPickupCost AS new_pickup_cost,
	DeliveryCost AS delivery_cost,
	NewDeliveryCost AS new_delivery_cost,
	AccessorialsValue AS accessorials_value,
	NewAccessorialsValue AS new_accessorials_value,
	AccessorialsPercentage AS accessorials_percentage,
	NewAccessorialsPercentage AS new_accessorials_percentage,
	IsActive AS is_active,
	IsInactiveViewable AS is_inactive_viewable,
	IsUpdated AS is_updated,
	ContextID AS context_id,
	PricingRates AS pricing_rates,
	WorkflowErrors AS workflow_errors
FROM dbo.RequestSectionLanePricingPoint_Staging RSLPP
WHERE RSLPP.RequestSectionLaneID = {0} AND RSLPP.ContextID = '{1}'
AND RSLPP.IsActive = 1 AND RSLPP.IsInactiveViewable = 1 
) AS Q FOR JSON AUTO, INCLUDE_NULL_VALUES) AS VARCHAR(MAX))
"""

GET_REQUEST_SECTION_LANE_CHANGES_COUNT = """
DECLARE @Count INT = 0;

SELECT @Count = @Count + ISNULL(SUM(CASE WHEN IsUpdated = 1 THEN 1 ELSE 0 END), 0)
FROM dbo.RequestSectionLane_Staging
WHERE RequestSectionID = {0} AND ContextID LIKE '{1}' AND IsActive = 1 AND IsInactiveViewable = 1

SELECT @Count = @Count + ISNULL(SUM(CASE WHEN IsUpdated = 1 THEN 1 ELSE 0 END), 0)
FROM dbo.RequestSectionLane RSL
INNER JOIN dbo.RequestSectionLanePricingPoint_Staging RSLPP ON RSL.RequestSectionLaneID = RSLPP.RequestSectionLaneID
WHERE RSL.RequestSectionID = {0} AND RSLPP.ContextID LIKE '{1}' AND RSL.IsActive = 1 AND RSL.IsInactiveViewable = 1
AND RSLPP.IsActive = 1 AND RSLPP.IsInactiveViewable = 1

SELECT CAST((SELECT * FROM (
SELECT @Count AS [count]
) AS Q FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS VARCHAR(MAX))
"""

GET_DASHBOARD_HEADER = """
DECLARE @UserID BIGINT = {0};
DECLARE @NumTotalRequest INT, @NumAwaitingAnalysis INT, @NumAwaitingApproval INT, @NumReadyForPublish INT, @NumTenders INT;
With A1 AS (
SELECT DISTINCT r.RequestID, rst.RequestStatusTypeName, rt.RequestTypeName
FROM dbo.Request r
INNER JOIN dbo.[User] u ON u.UserID = r.CurrentEditorID
INNER JOIN dbo.Persona p ON p.PersonaID = u.PersonaID
INNER JOIN dbo.RequestStatusType rst ON r.RequestStatusTypeID = rst.RequestStatusTypeID
INNER JOIN dbo.RequestInformation I ON R.RequestID = I.RequestID
INNER JOIN dbo.RequestType RT ON I.RequestTypeID = RT.RequestTypeID
WHERE r.IsActive = 1 AND r.IsInactiveViewable = 1
    AND p.PersonaName IN ('Pricing Analyst', 'Credit Analyst', 'Credit Manager', 'Partner Carrier', 'Pricing Manager')
    AND (UserID = @UserID OR
        UserID IN (SELECT UserID FROM dbo.[User] WHERE UserManagerID = @UserID)
))

SELECT @NumTotalRequest = (SELECT COUNT(*) FROM A1),
	@NumAwaitingAnalysis = (SELECT COUNT(*) FROM A1 WHERE a1.RequestStatusTypeName = 'With Pricing'),
	@NumAwaitingApproval = (SELECT COUNT(*) FROM a1 WHERE a1.RequestStatusTypeName IN ('Sales Review', 'With Partner Carrier')),
	@NumReadyForPublish = (SELECT COUNT(*) FROM a1 WHERE a1.RequestStatusTypeName = 'Ready for Publish'),
	@NumTenders = (SELECT COUNT(*) FROM A1 WHERE a1.RequestTypeName = 'Tender');

SELECT CAST((SELECT * FROM (
SELECT @NumTotalRequest AS num_total_request,
	@NumAwaitingAnalysis AS num_awaiting_analysis,
	@NumAwaitingApproval AS num_awaiting_approval,
	@NumReadyForPublish AS num_ready_for_publish,
	@NumTenders AS num_tenders
) AS Q FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS VARCHAR(MAX));
"""

GET_REQUEST_LIST = """
DECLARE @UserID BIGINT = {0};
DECLARE @UniType VARCHAR(50) = '{1}';
DECLARE @UserPersona VARCHAR(50);
SELECT @UserPersona = P.PersonaName FROM dbo.[User] U INNER JOIN dbo.Persona P ON U.PersonaID = P.PersonaID WHERE U.UserID = @UserID;
SELECT r.RequestCode, r.RequestID
FROM dbo.Request r
WHERE @UserPersona IN ('Pricing Analyst', 'Pricing Manager')
AND r.IsActive = 1 AND r.IsInactiveViewable = 1
AND (r.CurrentEditorID = @UserID OR
    r.CurrentEditorID IN (SELECT UserID FROM dbo.[User] WHERE UserManagerID = @UserID))
AND (R.UniType = @UniType OR R.UniType is NULL)
"""

GET_SPEEDSHEET_LIST = """
DECLARE @UserID BIGINT = {0};
DECLARE @UniType VARCHAR(50) = '{1}';
DECLARE @UserPersona VARCHAR(50);
SELECT @UserPersona = P.PersonaName FROM dbo.[User] U INNER JOIN dbo.Persona P ON U.PersonaID = P.PersonaID WHERE U.UserID = @UserID;

SELECT r.RequestCode, r.RequestID
FROM dbo.Request r
WHERE @UserPersona IN ('Sales Representative', 'Sales Manager', 'Sales Coordinator', 'Pricing Analyst', 'Pricing Manager')
AND r.IsActive = 1 AND r.IsInactiveViewable = 1
AND (r.CurrentEditorID = @UserID OR
    r.CurrentEditorID IN (SELECT UserID FROM dbo.[User] WHERE UserManagerID = @UserID) )
AND (r.UniType = @UniType OR r.UniType is NULL)
"""

GET_REQUEST = """
DECLARE @UserID BIGINT = {0};
DECLARE @UniType VARCHAR(50) = '{1}';
DECLARE @RequestId VARCHAR(50) = '{2}';
DECLARE @UserPersona VARCHAR(50);
SELECT @UserPersona = P.PersonaName FROM dbo.[User] U INNER JOIN dbo.Persona P ON U.PersonaID = P.PersonaID WHERE U.UserID = @UserID;

SELECT r.RequestCode, r.RequestID
FROM dbo.Request r
WHERE @UserPersona IN ('Pricing Analyst', 'Pricing Manager')
AND r.IsActive = 1 AND r.IsInactiveViewable = 1
AND (r.CurrentEditorID = @UserID OR
    r.CurrentEditorID IN (SELECT UserID FROM dbo.[User] WHERE UserManagerID = @UserID) )
AND r.RequestID = @RequestId 
AND (r.UniType = @UniType OR r.UniType is NULL)
"""

GET_PRICING_POINT_DESTINATION = """
DECLARE @OPC BIGINT;
DECLARE @DPC BIGINT;
DECLARE @RequestSectionLaneID BIGINT;

SELECT @OPC = OriginPostalCodeID,
	 @DPC = DestinationPostalCodeID,
	 @RequestSectionLaneID = RequestSectionLaneID
FROM dbo.RequestSectionLanePricingPoint
WHERE RequestSectionLanePricingPointID = {0};

WITH A AS (
SELECT PC.PostalCodeID, SP.ServicePointID, SP.BasingPointID, TSP.TerminalID, P.ProvinceID, R.RegionID, C.CountryID
FROM dbo.PostalCode PC 
INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
INNER JOIN dbo.TerminalServicePoint TSP ON TSP.ServicePointID = SP.ServicePointID
INNER JOIN dbo.Province P ON SP.ProvinceID = P.ProvinceID
INNER JOIN dbo.Region R ON P.RegionID = R.RegionID
INNER JOIN dbo.Country C ON R.CountryID = C.CountryID
WHERE PC.PostalCodeID = @OPC
), B AS (
SELECT PC.PostalCodeID, SP.ServicePointID, SP.BasingPointID, TSP.TerminalID, P.ProvinceID, R.RegionID, C.CountryID
FROM dbo.PostalCode PC 
INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
INNER JOIN dbo.TerminalServicePoint TSP ON TSP.ServicePointID = SP.ServicePointID
INNER JOIN dbo.Province P ON SP.ProvinceID = P.ProvinceID
INNER JOIN dbo.Region R ON P.RegionID = R.RegionID
INNER JOIN dbo.Country C ON R.CountryID = C.CountryID
WHERE PC.PostalCodeID = @DPC
), O AS (
SELECT RSL.*
FROM dbo.RequestSectionLane RSL 
WHERE RSL.RequestSectionID = {1}
AND ( 
		(RSL.OriginPointTypeName = 'Country' AND RSL.OriginCountryID IN (SELECT CountryID FROM A))
		OR (RSL.OriginPointTypeName = 'Region' AND RSL.OriginRegionID IN (SELECT RegionID FROM A))
		OR (RSL.OriginPointTypeName = 'Province' AND RSL.OriginProvinceID IN (SELECT ProvinceID FROM A))
		OR (RSL.OriginPointTypeName = 'Terminal' AND RSL.OriginTerminalID IN (SELECT TerminalID FROM A))
		OR (RSL.OriginPointTypeName = 'Basing Point' AND RSL.OriginBasingPointID IN (SELECT BasingPointID FROM A))
		OR (RSL.OriginPointTypeName = 'Service Point' AND RSL.OriginBasingPointID IN (SELECT ServicePointID FROM A))
		OR (RSL.OriginPointTypeName = 'Postal Code' AND RSL.OriginPostalCodeID IN (SELECT PostalCodeID FROM A))
	)
), D AS (
SELECT RSL.*
FROM dbo.RequestSectionLane RSL 
INNER JOIN O ON O.RequestSectionLaneID = RSL.RequestSectionLaneID
WHERE RSL.RequestSectionID = {1} 
AND ( 
		(RSL.DestinationPointTypeName = 'Country' AND RSL.DestinationCountryID IN (SELECT CountryID FROM B))
		OR (RSL.DestinationPointTypeName = 'Region' AND RSL.DestinationRegionID IN (SELECT RegionID FROM B))
		OR (RSL.DestinationPointTypeName = 'Province' AND RSL.DestinationProvinceID IN (SELECT ProvinceID FROM B))
		OR (RSL.DestinationPointTypeName = 'Terminal' AND RSL.DestinationTerminalID IN (SELECT TerminalID FROM B))
		OR (RSL.DestinationPointTypeName = 'Basing Point' AND RSL.DestinationBasingPointID IN (SELECT BasingPointID FROM B))
		OR (RSL.DestinationPointTypeName = 'Service Point' AND RSL.DestinationBasingPointID IN (SELECT ServicePointID FROM B))
		OR (RSL.DestinationPointTypeName = 'Postal Code' AND RSL.DestinationPostalCodeID IN (SELECT PostalCodeID FROM B))
	)
)

SELECT CAST((SELECT * FROM (
SELECT * FROM D
WHERE RequestSectionLaneID <> @RequestSectionLaneID
) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
"""

GET_REQUEST_HEADER = """
SET NOCOUNT ON;
DECLARE @UserID BIGINT = {1};
DECLARE @RequestID BIGINT = {0};
DECLARE @IsActionable BIT = 0;
DECLARE @SecondaryStatus NVARCHAR(MAX);
DECLARE @Approvals NVARCHAR(MAX);
DECLARE @IsCurrentEditor BIT;
DECLARE @CanRequestEditorRights BIT = 1;

IF EXISTS (SELECT TOP 1 NotificationID FROM dbo.RequestEditorRight WHERE RequestID = @RequestID AND UserID = @UserID AND IsActive = 1 AND IsInactiveViewable = 1)
SELECT @CanRequestEditorRights = 0;

IF (SELECT rst.RequestStatusTypeName FROM dbo.Request r
     INNER JOIN dbo.RequestStatusType rst ON rst.RequestStatusTypeID = r.RequestStatusTypeID
WHERE r.RequestID = @RequestID ) IN ('Published', 'Archived')
SELECT @CanRequestEditorRights = 0;


SELECT @IsCurrentEditor = CASE WHEN r.CurrentEditorID IS NOT NULL AND r.CurrentEditorID = @UserID THEN 1 ELSE 0 END
FROM dbo.Request r WHERE r.RequestID = @RequestID

SELECT CAST((SELECT * FROM (
SELECT R.RequestID,
	R.RequestCode AS request_code,
	RST.RequestStatusTypeName AS request_status_type,
	ISNULL(C.CustomerName,'') AS customer_name,
	ISNULL(A.AccountNumber, '') AS account_number,
	RH.VersionNum AS num_versions,
	SL.ServiceLevelID AS service_level_id,
	SL.ServiceLevelCode AS service_level_code,
	SL.PricingType,
	SL.PricingType AS service_level_pricing_type,
	SO.ServiceOfferingID AS service_offering_id,
	SO.ServiceOfferingName AS service_offering_name,
	ISNULL(RT.RequestTypeName, '') AS request_type_name,
	@IsCurrentEditor AS is_current_editor,
	curU.UserName CurrentEditorName,
	r.PricingAnalystID,
	r.ApproverID,
	CASE WHEN eq.DueDate IS NULL THEN 0 ELSE DATEDIFF(SECOND, GETDATE(), eq.DueDate) END PublishedInSeconds,
	ISNULL(r.PricingRunning, 0) PricingRunning,
	ISNULL(I.[Priority], 0) AS [priority],
	ISNULL(A.IsExtendedPayment, 0) AS is_extended_payment,
	@CanRequestEditorRights AS can_request_editor_rights,
	ISNULL(A.ExtendedPaymentDays, 0) AS extended_payment_days,
	I.RequestInformationID AS request_information_id,
	p.RequestProfileID AS request_profile_id
FROM dbo.Request R
LEFT JOIN dbo.Request_History RH ON R.RequestID = RH.RequestID AND RH.IsLatestVersion = 1
INNER JOIN dbo.RequestInformation I ON R.RequestID = I.RequestID
INNER JOIN dbo.RequestStatusType RST ON r.RequestStatusTypeID = RST.RequestStatusTypeID
INNER JOIN dbo.RequestProfile P ON R.RequestID = P.RequestID
INNER JOIN dbo.Customer C ON I.CustomerID = C.CustomerID
INNER JOIN dbo.ServiceLevel SL ON C.ServiceLevelID = SL.ServiceLevelID
INNER JOIN dbo.ServiceOffering SO ON SL.ServiceOfferingID = SO.ServiceOfferingID
LEFT JOIN dbo.[User] curU ON curU.UserID = r.CurrentEditorID
LEFT JOIN dbo.Account A ON C.AccountID = A.AccountID
LEFT JOIN dbo.RequestType RT ON I.RequestTypeID = RT.RequestTypeID
LEFT JOIN (SELECT RequestID, MAX(DueDate) DueDate FROM dbo.EngineQueue
    WHERE Completed = 0 AND OperationID = 3
    GROUP BY RequestID) eq ON eq.RequestID = r.RequestID
WHERE R.RequestID =  @RequestID
) AS Q FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS VARCHAR(MAX))
"""

GET_REQUEST_HEADER_HISTORY = """
SET NOCOUNT ON;
DECLARE @UserID BIGINT = {2};
DECLARE @VersionNum INT = {1}; 
DECLARE @RequestID BIGINT = {0};
DECLARE @IsActionable BIT = 0;
DECLARE @IsCurrentEditor BIT;
DECLARE @CanRequestEditorRights BIT = 1;

IF EXISTS (SELECT TOP 1 NotificationID FROM dbo.RequestEditorRight WHERE RequestID = @RequestID AND UserID = @UserID AND IsActive = 1 AND IsInactiveViewable = 1)
SELECT @CanRequestEditorRights = 0;

IF NOT EXISTS (SELECT RequestQueueID FROM dbo.RequestQueue WHERE RequestID = @RequestID
AND UserID = @UserID AND IsActive = 1 AND IsInactiveViewable = 1 AND CompletedON IS NULL)
SELECT @CanRequestEditorRights = 0;

DECLARE @Q AS TABLE 
(
	IsSecondary BIT NOT NULL,
	RequestStatusTypeID BIGINT NOT NULL,
	UserPersona NVARCHAR(50) NOT NULL,
	CompletedOn DATETIME2(7) NULL,
	UserID BIGINT NOT NULL,
	IsActionable BIT NOT NULL
)
INSERT INTO @Q
(
	IsSecondary,
	RequestStatusTypeID,
	UserPersona,
	CompletedOn,
	UserID,
	IsActionable
)
SELECT IsSecondary,
	RequestStatusTypeID,
	UserPersona,
	CompletedOn,
	UserID,
	IsActionable
FROM dbo.RequestQueue
WHERE RequestID = @RequestID  
AND IsActive = 1 AND IsInactiveViewable = 1 

SELECT @IsActionable = IsActionable
FROM dbo.RequestQueue 
WHERE RequestID = @RequestID AND UserID = @UserID AND CompletedOn IS NULL

SELECT @IsCurrentEditor = CASE WHEN RS.CurrentEditorID IS NOT NULL AND RS.CurrentEditorID = @UserID THEN 1 ELSE 0 END
FROM dbo.RequestStatus RS WHERE RS.RequestID = @RequestID

SELECT CAST((SELECT * FROM (
SELECT R.RequestID,
	RH.RequestCode AS request_code,
	RST.RequestStatusTypeName AS request_status_type,
	CASE WHEN IH.VersionNum > 1 THEN 1 ELSE 0 END information_tab,
	CASE WHEN PH.VersionNum > 1 THEN 1 ELSE 0 END profile_tab,
	ISNULL(C.CustomerName,'') AS customer_name,
	ISNULL(A.AccountNumber,'') AS account_number,
	R.VersionNum AS num_versions,
	SL.ServiceLevelID AS service_level_id,
	SL.ServiceLevelCode AS service_level_code,
	SL.PricingType AS service_level_pricing_type,
	SO.ServiceOfferingID AS service_offering_id,
	SO.ServiceOfferingName AS service_offering_name,
	ISNULL(RT.RequestTypeName, '') AS request_type_name,
	@IsCurrentEditor AS is_current_editor,
	ISNULL(IH.[Priority], 0) AS [priority],
	ISNULL(A.IsExtendedPayment, 0) AS is_extended_payment,
	'[]' AS secondary_statuses,
	'[]' AS actionable_approvals,
	ISNULL(@IsActionable, 0) AS is_actionable,
	@CanRequestEditorRights AS can_request_editor_rights,
	ISNULL(A.ExtendedPaymentDays, 0) AS extended_payment_days,
	IH.RequestInformationID AS request_information_id,
	PH.RequestProfileID AS request_profile_id
FROM dbo.Request_History R 
INNER JOIN dbo.Request_History RH ON R.RequestID = RH.RequestID AND RH.VersionNum = @VersionNum
INNER JOIN dbo.RequestStatus RS ON R.RequestID = RS.RequestID
INNER JOIN dbo.RequestStatusType RST ON RS.RequestStatusTypeID = RST.RequestStatusTypeID
INNER JOIN dbo.RequestInformation_History IH ON RH.RequestInformationVersionID = IH.RequestInformationVersionID
INNER JOIN dbo.RequestProfile_History PH ON RH.RequestProfileVersionID = PH.RequestProfileVersionID
INNER JOIN dbo.Customer_History C ON IH.CustomerVersionID = C.CustomerVersionID
INNER JOIN dbo.ServiceLevel_History SL ON C.ServiceLevelVersionID = SL.ServiceLevelVersionID
INNER JOIN dbo.ServiceOffering_History SO ON SL.ServiceOfferingVersionID = SO.ServiceOfferingVersionID
LEFT JOIN dbo.Account_History A ON C.AccountVersionID = A.AccountVersionID
LEFT JOIN dbo.RequestType_History RT ON IH.RequestTypeVersionID = RT.RequestTypeVersionID
WHERE R.RequestID = @RequestID AND R.IsLatestVersion = 1
) AS Q FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS VARCHAR(MAX))
"""

RESOLVE_NAME_TO_ID = """
DECLARE @ID CHAR(32)
SET @ID = '{0}'
SELECT RSLIQ.RequestSectionID                as RequestSectionID,
       OGRSLPT.RequestSectionLanePointTypeID as OriginGroupTypeID,
       CASE
           WHEN OGRSLPT.RequestSectionLanePointTypeName = 'Country' THEN
               (SELECT C.CountryID
                FROM dbo.Country C
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON C.CountryCode = RSLIQ.OriginGroupCode
                WHERE RSLIQ.id = @ID)

           WHEN OGRSLPT.RequestSectionLanePointTypeName = 'Region' THEN
               (SELECT R.RegionID
                FROM dbo.Region R
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON R.RegionCode = RSLIQ.OriginGroupCode
                WHERE RSLIQ.id = @ID)

           WHEN OGRSLPT.RequestSectionLanePointTypeName = 'Province' THEN
               (SELECT P.ProvinceID
                FROM dbo.Province P
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON P.ProvinceCode = RSLIQ.OriginGroupCode
                WHERE RSLIQ.id = @ID)
           END                               as OriginGroupID,
       OPRSLPT.RequestSectionLanePointTypeID as OriginPointTypeID,
       CASE
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Country' THEN
               (SELECT C.CountryID
                FROM dbo.Country C
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON C.CountryCode = RSLIQ.OriginPointCode
                WHERE RSLIQ.id = @ID)
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Region' THEN
               (SELECT R.RegionID
                FROM dbo.Region R
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON R.RegionCode = RSLIQ.OriginPointCode
                WHERE RSLIQ.id = @ID)
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Province' THEN
               (SELECT P.ProvinceID
                FROM dbo.Province P
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON P.ProvinceCode = RSLIQ.OriginPointCode
                WHERE RSLIQ.id = @ID)
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Terminal' THEN
               (SELECT T.TerminalID
                FROM dbo.Terminal T
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON T.TerminalCode = RSLIQ.OriginPointCode
                WHERE RSLIQ.id = @ID)
            -- Add logic to ensure correct basing point match
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Basing Point' THEN
               (SELECT BP.BasingPointID
                FROM dbo.BasingPoint BP
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON BP.BasingPointName = RSLIQ.OriginPointCode
						 -- Inner Join dbo.Province P
							-- 		ON P.ProvinceCode = RSLIQ.OriginGroupCode
                WHERE RSLIQ.id = @ID)
				-- AND P.ProvinceID = BP.ProvinceID)
            -- Add logic to ensure correct service point match
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Service Point' THEN
               (Select SP.ServicePointID
                FROM dbo.ServicePoint SP
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON SP.ServicePointName = RSLIQ.OriginPointCode
						-- Inner Join dbo.Province P
						-- 			ON P.ProvinceCode = RSLIQ.OriginGroupCode
                WHERE RSLIQ.id = @ID)
				-- AND P.ProvinceID = SP.ProvinceID)
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Postal Code' THEN
               (Select PC.PostalCodeID
                FROM dbo.PostalCode PC
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON PC.PostalCodeName = RSLIQ.OriginPointCode
                WHERE RSLIQ.id = @ID)
           END                               as OriginPointID,
       DGRSLPT.RequestSectionLanePointTypeID as DestinationGroupTypeID,


       CASE
           WHEN DGRSLPT.RequestSectionLanePointTypeName = 'Country' THEN
               (Select C.CountryID
                FROM dbo.Country C
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON C.CountryCode = RSLIQ.DestinationGroupCode
                WHERE RSLIQ.id = @ID)
           WHEN DGRSLPT.RequestSectionLanePointTypeName = 'Region' THEN
               (Select R.RegionID
                FROM dbo.Region R
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON R.RegionCode = RSLIQ.DestinationGroupCode
                WHERE RSLIQ.id = @ID)
           WHEN DGRSLPT.RequestSectionLanePointTypeName = 'Province' THEN
               (Select P.ProvinceID
                FROM dbo.Province P
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON P.ProvinceCode = RSLIQ.DestinationGroupCode
                WHERE RSLIQ.id = @ID)
           END                               as DestinationGroupID,
       DPRSLPT.RequestSectionLanePointTypeID as DestinationPointTypeID,

       CASE
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Country' THEN
               (Select C.CountryID
                FROM dbo.Country C
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON C.CountryCode = RSLIQ.DestinationPointCode
                WHERE RSLIQ.id = @ID)
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Region' THEN
               (Select R.RegionID
                FROM dbo.Region R
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON R.RegionCode = RSLIQ.DestinationPointCode
                WHERE RSLIQ.id = @ID)
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Province' THEN
               (Select P.ProvinceID
                FROM dbo.Province P
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON P.ProvinceCode = RSLIQ.DestinationPointCode
                WHERE RSLIQ.id = @ID)
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Terminal' THEN
               (Select T.TerminalID
                FROM dbo.Terminal T
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON T.TerminalCode = RSLIQ.DestinationPointCode
                WHERE RSLIQ.id = @ID)
            -- Add logic to ensure correct basing point match
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Basing Point' THEN
               (Select BP.BasingPointID
                FROM dbo.BasingPoint BP
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON BP.BasingPointName = RSLIQ.DestinationPointCode
						 -- Inner Join dbo.Province P
							-- 		ON P.ProvinceCode = RSLIQ.DestinationGroupCode

                WHERE RSLIQ.id = @ID)
				-- AND P.ProvinceID = BP.ProvinceID)
            -- Add logic to ensure correct service point match
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Service Point' THEN
               (SELECT SP.ServicePointID
                FROM dbo.ServicePoint SP
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON SP.ServicePointName = RSLIQ.DestinationPointCode
						 -- Inner Join dbo.Province P
							-- 		ON P.ProvinceCode = RSLIQ.DestinationGroupCode
                WHERE RSLIQ.id = @ID)
				-- AND P.ProvinceID = SP.ProvinceID)
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Postal Code' THEN
               (Select PC.PostalCodeID
                FROM dbo.PostalCode PC
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON PC.PostalCodeName = RSLIQ.DestinationPointCode
                WHERE RSLIQ.id = @ID)
           END                               as DestinationPointID,
       RSLIQ.IsBetween

FROM dbo.RequestSectionLaneImportQueue RSLIQ
         INNER JOIN dbo.RequestSection RS ON RS.RequestSectionID = RSLIQ.RequestSectionID
         INNER JOIN dbo.SubServiceLevel SSLL ON RS.SubServiceLevelID = SSLL.SubServiceLevelID
         INNER JOIN dbo.ServiceLevel SL ON SSLL.ServiceLevelID = SL.ServiceLevelID
         INNER JOIN dbo.RequestSectionLanePointType OGRSLPT
                    ON OGRSLPT.RequestSectionLanePointTypeName = RSLIQ.OriginGroupTypeName
         INNER JOIN dbo.RequestSectionLanePointType OPRSLPT
                    ON OPRSLPT.RequestSectionLanePointTypeName = RSLIQ.OriginPointTypeName
         INNER JOIN dbo.RequestSectionLanePointType DGRSLPT
                    ON DGRSLPT.RequestSectionLanePointTypeName = RSLIQ.DestinationGroupTypeName
         INNER JOIN dbo.RequestSectionLanePointType DPRSLPT
                    ON DPRSLPT.RequestSectionLanePointTypeName = RSLIQ.DestinationPointTypeName

WHERE RSLIQ.id = @id
  AND -- We only need to run RequestSectionLane_Insert for NEW LANES ONLY
    RS.IsDensityPricing = OGRSLPT.IsDensityPricing
  AND RS.IsDensityPricing = OPRSLPT.IsDensityPricing
  AND RS.IsDensityPricing = DGRSLPT.IsDensityPricing
  AND RS.IsDensityPricing = DPRSLPT.IsDensityPricing
  AND OGRSLPT.IsGroupType = 1
  AND DGRSLPT.IsGroupType = 1
  AND OPRSLPT.IsPointType = 1
  AND DPRSLPT.IsPointType = 1
  AND OGRSLPT.LocationHierarchy <= OPRSLPT.LocationHierarchy
  AND DGRSLPT.LocationHierarchy <= DPRSLPT.LocationHierarchy
  AND OPRSLPT.ServiceOfferingID = SL.ServiceOfferingID
  AND OGRSLPT.ServiceOfferingID = SL.ServiceOfferingID
  AND DPRSLPT.ServiceOfferingID = SL.ServiceOfferingID
  AND DGRSLPT.ServiceOfferingID = SL.ServiceOfferingID
  AND RS.IsActive = 1
  AND RS.IsInactiveViewable = 1
  AND SL.IsActive = 1
  AND SL.IsInactiveViewable = 1
  AND SSLL.IsActive = 1
  AND SSLL.IsInactiveViewable = 1
  AND OGRSLPT.IsActive = 1
  AND OGRSLPT.IsInactiveViewable = 1
  AND OPRSLPT.IsActive = 1
  AND OPRSLPT.IsInactiveViewable = 1
  AND DGRSLPT.IsActive = 1
  AND DGRSLPT.IsInactiveViewable = 1
  AND DPRSLPT.IsActive = 1
  AND DPRSLPT.IsInactiveViewable = 1"""

# -- For Pricing Point Template we need to convert the following values from RequestSectionLanePricingPointImportQueue into the IDs to use with RequestSectionLanePricingPoint_Insert Stored Procedure for NEW Pricing Points ONLY
RESOLVE_PP_NAME_TO_ID = """
DECLARE @ID CHAR(32)
SET @ID = '{0}'
SELECT RSLPPIQ.RequestSectionID     as RequestSectionID,
       RSLPPIQ.RequestSectionLaneID as RequestSectionLaneID,
       OPC.PostalCodeID             as OriginPostalCodeID,
       DPC.PostalCodeID             as DestinationPostalCodeID
FROM dbo.RequestSectionLanePricingPointImportQueue RSLPPIQ
         INNER JOIN dbo.RequestSection RS ON RS.RequestSectionID = RSLPPIQ.RequestSectionID
         INNER JOIN dbo.RequestSectionLane RSL ON RSL.RequestSectionLaneID = RSLPPIQ.RequestSectionLaneID
         INNER JOIN dbo.PostalCode OPC ON RSLPPIQ.OriginPostalCodeName = OPC.PostalCodeName
         INNER JOIN dbo.PostalCode DPC ON RSLPPIQ.DestinationPostalCodeName = DPC.PostalCodeName
WHERE RSLPPIQ.id = @ID
  AND RS.IsDensityPricing=0
  AND RSL.OriginCode = RSLPPIQ.OriginPointCode
  AND RSL.DestinationCode = RSLPPIQ.DestinationPointCode
  AND RS.IsActive = 1
  AND RS.IsInactiveViewable = 1
  AND RSL.IsActive = 1
  AND RSL.IsInactiveViewable = 1
  AND OPC.IsActive = 1
  AND OPC.IsInactiveViewable = 1
  AND DPC.IsActive = 1
  AND DPC.IsInactiveViewable = 1"""

RATE_BASE_SEARCH_BY_DESCRIPTION = """
    SELECT CAST((
    SELECT * FROM (
        SELECT DISTINCT [Description]
        ,[EffectiveDate]
        ,[RateBaseID]
        FROM [dbo].[RateBase]
        WHERE [IsActive] = 1 AND [IsInactiveViewable] = 1
        AND Description LIKE '{0}%'
        ) AS C FOR JSON AUTO)
    AS VARCHAR(MAX))
"""
