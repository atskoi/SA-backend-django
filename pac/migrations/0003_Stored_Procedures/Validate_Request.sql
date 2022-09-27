CREATE OR ALTER PROCEDURE [dbo].[Validate_Request]
	@RequestID BIGINT
AS
SET NOCOUNT ON;
    DECLARE @IsWithPricing INT;
    DECLARE @EffectiveValid INT;
    DECLARE @ExpiryValid INT;
    DECLARE @ValidationMessages TABLE(
        Message VARCHAR(200)
    )

    SELECT
        @IsWithPricing = CASE WHEN r.RequestStatusTypeID = 2 THEN 1 ELSE 0 END,
        @EffectiveValid = CASE WHEN ri.EffectiveDate >= getDate() THEN 1 ELSE 0 END,
        @ExpiryValid = CASE WHEN ri.ExpiryDate >= ri.EffectiveDate THEN 1 ELSE 0 END
    FROM dbo.Request r
    INNER JOIN dbo.RequestInformation ri ON ri.RequestID = r.RequestID
    WHERE r.RequestID = @RequestID;
    IF @IsWithPricing = 0
        INSERT INTO @ValidationMessages SELECT 'The Request is not With Pricing and cannot be published';
    IF @EffectiveValid = 0
        INSERT INTO @ValidationMessages SELECT 'The Request Effective Date is not in the future';
    IF @ExpiryValid = 0
        INSERT INTO @ValidationMessages SELECT 'The Request Expiry Date is not after the Effective Date';

    -- TODO: check that dbo.RequestInformation -> Customer -> Account ERP values match the ones in Account

    INSERT INTO @ValidationMessages
    SELECT DISTINCT CONCAT('There are unresolved errors in lanes for section: ', rs.SectionName) errors
    FROM dbo.Request r
    INNER JOIN dbo.RequestSection rs ON rs.RequestID = r.RequestID
    INNER JOIN dbo.RequestSectionLane rsl ON rsl.RequestSectionID = rs.RequestSectionID
    LEFT JOIN dbo.RequestSectionLanePricingPoint pp ON pp.RequestSectionLaneID = rsl.RequestSectionLaneID
    WHERE r.RequestID = @RequestID AND (rsl.WorkflowErrors IS NOT NULL OR pp.WorkflowErrors IS NOT NULL);

    SELECT * FROM @ValidationMessages;


