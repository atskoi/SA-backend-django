DECLARE @CountNonCustomer INT = 0;
SELECT @CountNonCustomer = COUNT(1) FROM dbo.Account WHERE AccountNumber = 0;
IF @CountNonCustomer = 0 BEGIN
    INSERT INTO [dbo].[Account] ([IsActive],[IsInactiveViewable],[AccountNumber],[AccountName],[AccountAlias],[AddressLine1],[AddressLine2]
    ,[PostalCode],[ContactName],[ContactTitle],[Phone],[Email],[Website],[AccountOwnerID],[ServicePointID],[ExternalCityName],[ExternalERPID])
     VALUES
    (0, 0, 0, 'Non Customer Tariff', NULL, 'Non Customer Tariff Account', NULL, '000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
END
EXEC dbo.Fill_Audit_Table @TableName = 'Account';