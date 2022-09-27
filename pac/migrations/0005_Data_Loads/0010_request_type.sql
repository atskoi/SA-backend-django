-- this table is almost completely phased out of use
MERGE INTO dbo.RequestType AS tgt
USING (VALUES
        (1, 1, 'Commitment',0,0,1),
        (1, 1, 'Cost+',0,0,0),
        (1, 1, 'Revision',0,1,0),
        (1, 1, 'Tender',0,0,1)
        )
       as src ([IsActive],[IsInactiveViewable],[RequestTypeName],[ApplyToCustomerUnderReview],[ApplyToRevision],[AllowSalesCommitment])
ON tgt.RequestTypeName = src.RequestTypeName
WHEN NOT MATCHED BY TARGET THEN
    INSERT ([IsActive],[IsInactiveViewable],[RequestTypeName],[ApplyToCustomerUnderReview],[ApplyToRevision],[AllowSalesCommitment])
    VALUES (src.IsActive, src.IsInactiveViewable, src.RequestTypeName,src.ApplyToCustomerUnderReview,src.ApplyToRevision,src.AllowSalesCommitment);
EXEC dbo.Fill_Audit_Table @TableName = 'RequestType';

