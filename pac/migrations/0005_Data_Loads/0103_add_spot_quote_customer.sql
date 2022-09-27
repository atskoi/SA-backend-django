DECLARE @NewAccountID BIGINT;
DECLARE @DefaultSL BIGINT;
MERGE dbo.Account AS tgt
USING (SELECT 1 IsActive,1 IsInactiveViewable, -1 AccountNumber,'Spot Quote Account' AccountName,
    'SalesForce' AddressLine1,'00000' PostalCode, 'SPOT-QUOTE' ExternalERPID) as src
ON (tgt.ExternalERPID = src.ExternalERPID)
WHEN NOT MATCHED THEN
    INSERT (IsActive,IsInactiveViewable,AccountNumber,AccountName,AddressLine1,PostalCode, ExternalERPID)
    VALUES (src.IsActive,src.IsInactiveViewable,src.AccountNumber,src.AccountName,src.AddressLine1,src.PostalCode, src.ExternalERPID)
;
SELECT @NewAccountID = AccountID FROM dbo.Account WHERE ExternalERPID = 'SPOT-QUOTE';
SELECT top(1) @DefaultSL = ServiceLevelID FROM dbo.ServiceLevel;

MERGE dbo.Customer AS tgt
USING (SELECT 1 IsActive, 1 IsInactiveViewable, 'Spot Quote Customer' CustomerName, 1 IsValidData, @NewAccountID AccountID, @DefaultSL ServiceLevelID) as src
ON (tgt.AccountID = src.AccountID)
WHEN NOT MATCHED THEN
    INSERT (IsActive,IsInactiveViewable,CustomerName,IsValidData,AccountID,ServiceLevelID )
    VALUES (src.IsActive,src.IsInactiveViewable,src.CustomerName,src.IsValidData,src.AccountID,src.ServiceLevelID)
;