MERGE INTO dbo.ServiceOffering AS tgt
USING (VALUES
        (1, 1, 'Freight'),
        (1, 1, 'SameDay')
        )
       as src ([IsActive],[IsInactiveViewable],[ServiceOfferingName])
ON tgt.ServiceOfferingName = src.ServiceOfferingName
WHEN NOT MATCHED BY TARGET THEN
    INSERT ([IsActive],[IsInactiveViewable],[ServiceOfferingName])
    VALUES (src.IsActive, src.IsInactiveViewable, src.ServiceOfferingName);
EXEC dbo.Fill_Audit_Table @TableName = 'ServiceOffering';