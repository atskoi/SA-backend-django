MERGE dbo.ServiceType AS tgt
USING (select 'Direct' ServiceClass, 'CARTAGE' ServiceTypeName, 'Direct Cartage' ServiceTypeDescription
    UNION ALL SELECT 'Direct', 'DIRECT', 'Direct'
    UNION ALL SELECT 'Indirect', 'EMBARGO', 'Temporary Embargo Zone'
    UNION ALL SELECT 'Indirect', 'INDIRECT', 'Indirect'
    UNION ALL SELECT 'Indirect', 'NOSERVICE', 'No Service Zone'
    UNION ALL SELECT 'Indirect', 'QUOTERQD', 'Requires Quote'
    ) as src
ON (tgt.ServiceTypeName LIKE src.ServiceTypeName)
WHEN MATCHED THEN
    UPDATE SET IsActive = 1, ISInactiveViewable = 1, ServiceClass = src.ServiceClass,
        ServiceTypeName = src.ServiceTypeName, ServiceTypeDescription = src.ServiceTypeDescription
WHEN NOT MATCHED THEN
    INSERT (IsActive, ISInactiveViewable, ServiceClass, ServiceTypeName, ServiceTypeDescription)
    VALUES (1, 1, src.ServiceClass, src.ServiceTypeName, src.ServiceTypeDescription)
  ;
  EXEC dbo.Fill_Audit_Table @TableName = 'ServiceType';