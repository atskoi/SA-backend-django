MERGE INTO dbo.PointType AS tgt
USING (VALUES
        ( 1, 1, 'Country', 1),
        ( 1, 1, 'Region', 2),
        ( 1, 1, 'Province', 3),
        ( 1, 1, 'Basing Point', 5),
        ( 1, 1, 'Service Point', 6),
        ( 1, 1, 'Terminal', 7),
        ( 1, 1, 'Postal Code', 8),
        ( 1, 1, 'Customer Zone', 4))
       as src (IsActive, IsInactiveViewable, PointTypeName, OrderID)
ON tgt.PointTypeName = src.PointTypeName
WHEN MATCHED THEN
UPDATE SET PointTypeOrderId = src.OrderID
WHEN NOT MATCHED BY TARGET THEN
INSERT ([IsActive],[IsInactiveViewable],[PointTypeName],[PointTypeOrderID])
VALUES (IsActive, IsInactiveViewable, PointTypeName, OrderID);
EXEC dbo.Fill_Audit_Table @TableName = 'PointType';
