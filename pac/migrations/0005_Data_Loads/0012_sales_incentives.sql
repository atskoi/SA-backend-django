MERGE INTO dbo.SalesIncentive AS tgt
USING (VALUES
        (1, 1, 'Increase'), 
        (1, 1, 'Legacy Account'), 
        (1, 1, 'Negotiate'),
        (1, 1, 'Decrease'),
        (1, 1, 'Hold'),
        (1, 1, 'Redo'),
        (1, 1, 'Cancel')
        )
       as src ([IsActive],[IsInactiveViewable],[SalesIncentiveType])
ON tgt.SalesIncentiveType = src.SalesIncentiveType
WHEN NOT MATCHED BY TARGET THEN
    INSERT ([IsActive],[IsInactiveViewable],[SalesIncentiveType])
    VALUES (src.IsActive, src.IsInactiveViewable, src.SalesIncentiveType);
EXEC dbo.Fill_Audit_Table @TableName = 'SalesIncentive';