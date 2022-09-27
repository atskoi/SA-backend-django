MERGE INTO dbo.Currency AS tgt
USING (VALUES
        (1, 1, 'Canadian Dollar', 'CAD'),
        (1, 1, 'US Dollar', 'USD')
        )
       as src ([IsActive],[IsInactiveViewable],[CurrencyName], [CurrencyCode])
ON tgt.CurrencyCode = src.CurrencyCode
WHEN NOT MATCHED BY TARGET THEN
    INSERT ([IsActive],[IsInactiveViewable],[CurrencyName], [CurrencyCode])
    VALUES (src.IsActive, src.IsInactiveViewable, src.CurrencyName, src.CurrencyCode);
EXEC dbo.Fill_Audit_Table @TableName = 'Currency';