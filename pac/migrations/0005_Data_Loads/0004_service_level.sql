DECLARE @FreightID INT = 0;
DECLARE @SamedayID INT = 0;
SELECT @FreightID = ServiceOfferingID from dbo.ServiceOffering WHERE ServiceOfferingName = 'Freight';
SELECT @SamedayID = ServiceOfferingID from dbo.ServiceOffering WHERE ServiceOfferingName = 'SameDay';

MERGE INTO dbo.ServiceLevel AS tgt
USING (VALUES
        (1, 1, 'Domestic LTL', 'DL', 'DOMESTIC-LTL-SAMEDAY', @FreightID),
        (1, 1, 'US Cross-Border', 'CB', 'CBLTL', @FreightID),
        (1, 1, 'Residential', 'RS', 'Domestic-LTL-Sameday', @SamedayID),
        (1, 1, 'TL', 'TL', 'Other', @FreightID),
        (1, 1, 'SCS', 'SO', 'Other', @FreightID),
        (1, 1, 'Flatbed', 'FB', 'Other', @FreightID),
        (1, 1, 'LTL Air', 'LA', 'DOMESTIC-LTL-SAMEDAY', @SamedayID)
        )
       as src ([IsActive],[IsInactiveViewable],[ServiceLevelName],[ServiceLevelCode],[PricingType],[ServiceOfferingID])
ON tgt.ServiceLevelName = src.ServiceLevelName
WHEN NOT MATCHED BY TARGET THEN
    INSERT ([IsActive],[IsInactiveViewable],[ServiceLevelName],[ServiceLevelCode],[PricingType],[ServiceOfferingID])
    VALUES (src.IsActive, src.IsInactiveViewable, src.ServiceLevelName, src.ServiceLevelCode, src.PricingType, src.ServiceOfferingID);
EXEC dbo.Fill_Audit_Table @TableName = 'ServiceLevel';
