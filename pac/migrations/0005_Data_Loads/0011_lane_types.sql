MERGE INTO dbo.LaneType AS tgt
USING (VALUES
        (1, 1, 'All'),
        (1, 1, 'Total Profitable'),
        (1, 1, 'Total Non-Profitable'),
        (1, 1, 'Catch-all Profitable'),
        (1, 1, 'Catch-all Non-Profitable'))
       as src ([IsActive],[IsInactiveViewable],[LaneTypeName])
ON tgt.LaneTypeName = src.LaneTypeName
WHEN NOT MATCHED BY TARGET THEN
    INSERT ([IsActive],[IsInactiveViewable],[LaneTypeName])
    VALUES (src.IsActive, src.IsInactiveViewable, src.LaneTypeName);
EXEC dbo.Fill_Audit_Table @TableName = 'LaneType';
