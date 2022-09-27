MERGE INTO dbo.EngineOperation AS tgt
USING (VALUES
        ('Price Lanes'),
        ('Check Impacts'),
        ('Publish To TM'),
        ('Check RRF Expiry For GRI Review')
        )
       as src ([OperationName])
ON tgt.OperationName = src.OperationName
WHEN NOT MATCHED BY TARGET THEN
    INSERT ([OperationName])
    VALUES (src.OperationName);
EXEC dbo.Fill_Audit_Table @TableName = 'EngineOperation';
