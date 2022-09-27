MERGE INTO dbo.Language AS tgt
USING (VALUES
        (1, 1, 'English', 'EN'),
        (1, 1, 'French', 'FR')
        )
       as src ([IsActive],[IsInactiveViewable],[LanguageName], [LanguageCode])
ON tgt.LanguageCode = src.LanguageCode
WHEN NOT MATCHED BY TARGET THEN
    INSERT ([IsActive],[IsInactiveViewable],[LanguageName], [LanguageCode])
    VALUES (src.IsActive, src.IsInactiveViewable, src.LanguageName, src.LanguageCode);
EXEC dbo.Fill_Audit_Table @TableName = 'Language';
