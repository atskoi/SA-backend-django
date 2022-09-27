MERGE INTO dbo.Persona AS tgt
USING (VALUES
        (1, 1, 'Admin'),
        (1, 1, 'Credit Analyst'),
        (1, 1, 'Credit Manager'),
        (1, 1, 'Partner Carrier'),
        (1, 1, 'Pricing Analyst'),
        (1, 1, 'Pricing Manager'),
        (1, 1, 'Review Analyst'),
        (1, 1, 'Sales Coordinator'),
        (1, 1, 'Sales Manager'),
        (1, 1, 'Sales Representative'),
        (1, 1, 'Spot Quote Analyst'),
        (1, 1, 'VP of Pricing'),
        (1, 1, 'VP of Sales'),
        (1, 1, 'External Viewer')
        )
       as src ([IsActive],[IsInactiveViewable],[PersonaName])
ON tgt.PersonaName = src.PersonaName
WHEN NOT MATCHED BY TARGET THEN
    INSERT ([IsActive],[IsInactiveViewable],[PersonaName])
    VALUES (src.IsActive, src.IsInactiveViewable, src.PersonaName);
EXEC dbo.Fill_Audit_Table @TableName = 'Persona';



