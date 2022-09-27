CREATE OR ALTER PROCEDURE [dbo].[RequestInformation_Insert]
	@RequestID        BIGINT,
	@CustomerID        BIGINT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL,
	@LanguageID BIGINT=NULl,
	@RequestInformationID NVARCHAR (32) output
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @RequestInformation table 
( 
    [RequestInformationID]          BIGINT        NOT NULL,
    [RequestID]        BIGINT NOT NULL,
    [CustomerID]                BIGINT   NOT NULL,
	[IsValidData]	BIT NOT NULL,
	[LanguageID]    BIGINT
)

BEGIN TRAN

INSERT INTO [dbo].[RequestInformation]
([RequestID],
 [CustomerID],
 [IsValidData],
 [IsActive],
 [IsInactiveViewable],
 [LanguageID],
 [RequestTypeID],
 [EffectiveDate],
 [ExpiryDate],
 [CurrencyID])
OUTPUT INSERTED.[RequestInformationID], INSERTED.[RequestID], INSERTED.[CustomerID], INSERTED.[IsValidData], INSERTED.[LanguageID] INTO @RequestInformation
    (
     [RequestInformationID],
     [RequestID],
     [CustomerID],
     [IsValidData],
     [LanguageID]
        )
VALUES (@RequestID,
        @CustomerID,
        0,
        1,
        1,
        @LanguageID,
        2,
        cast (GETDATE() as DATE),
        CAST(DATEADD(year, 1, GETDATE()) as date),
        1
        )

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[RequestInformation_History]
([RequestInformationID],
 [RequestVersionID],
 [CustomerVersionID],
 [IsValidData],
 [IsActive],
 [VersionNum],
 [IsLatestVersion],
 [IsInactiveViewable],
 [UpdatedOn],
 [UpdatedBy],
 [Comments],
 [EffectiveDate],
 [ExpiryDate],
 [CurrencyVersionID])
SELECT R.[RequestInformationID],
       rh.[RequestVersionID],
       CH.[CustomerVersionID],
       R.[IsValidData],
       1,
       1,
       1,
       1,
       GETUTCDATE(),
       @UpdatedBy,
       @Comments,
       cast (GETDATE() as DATE),
       CAST(DATEADD(year, 1, GETDATE()) as date),
       1
FROM @RequestInformation R
         INNER JOIN dbo.Customer_History CH ON R.CustomerID = CH.CustomerID AND CH.IsLatestVersion = 1
         INNER JOIN dbo.Request_History rh ON rh.RequestID = r.RequestID AND rh.IsLatestVersion = 1

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT 

SELECT @RequestInformationID = R.RequestInformationID
FROM @RequestInformation R
WHERE R.CustomerID = @CustomerID

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0)

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN
	END

IF (@ROWCOUNT1 <> 1) OR (@ROWCOUNT2 <> 1)
	
	BEGIN
	ROLLBACK TRAN
	IF (@ROWCOUNT1 <> 1)
		RAISERROR('%d Records Affected by Insert Procedure!', 16, 1, @ROWCOUNT1);
	IF (@ROWCOUNT2 <> 1)
		RAISERROR('%d Records Affected by Insert Procedure!', 16, 1, @ROWCOUNT2);
	RETURN
	END

COMMIT TRAN

