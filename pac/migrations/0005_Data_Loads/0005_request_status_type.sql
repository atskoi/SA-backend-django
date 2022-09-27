SET IDENTITY_INSERT dbo.RequestStatusType ON;
MERGE INTO dbo.RequestStatusType AS tgt
USING (VALUES
        ( 1, 1, 'Initiated', 1),
        ( 1, 1, 'With Pricing', 2),
        ( 1, 1, 'Cost+ Analysis', 3),
        ( 1, 1, 'With Partner Carrier', 4),
        ( 1, 1, 'Sales Review', 5),
        ( 1, 1, 'Publish Queued', 6),
        ( 1, 1, 'Ready for Publish', 7),
        ( 1, 1, 'Published', 8),
        ( 1, 1, 'Declined', 9),
        ( 1, 1, 'Annual Review', 10),
        ( 1, 1, 'In Review Approval', 11),
        ( 1, 1, 'Credit Analysis', 12),
        ( 1, 1, 'Archived', 13),
        ( 1, 1, 'Spot Quote', 14),
        ( 1, 1, 'Approve for Publishing', 15)
        )
       as src (IsActive, IsInactiveViewable, RequestStatusTypeName, RequestStatusTypeID)
ON tgt.RequestStatusTypeID = src.RequestStatusTypeID
WHEN MATCHED THEN
UPDATE SET RequestStatusTypeName = src.RequestStatusTypeName
WHEN NOT MATCHED THEN
    INSERT (IsActive, IsInactiveViewable, RequestStatusTypeName, RequestStatusTypeID)
    VALUES (src.IsActive, src.IsInactiveViewable, src.RequestStatusTypeName, src.RequestStatusTypeID)
    ;
SET IDENTITY_INSERT dbo.RequestStatusType OFF;
EXEC dbo.Fill_Audit_Table @TableName = 'RequestStatusType';
