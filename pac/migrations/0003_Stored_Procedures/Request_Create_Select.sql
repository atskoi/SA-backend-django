CREATE OR ALTER PROCEDURE [dbo].[Request_Create_Select]
	@UserID BIGINT,
	@ServiceLevelID BIGINT,
	@AccountID BIGINT = NULL,
	@OutputRequestID BIGINT output,
	@IsNewRequest BIT output,
	@SpeedSheetName NVARCHAR(MAX)=NULL,
	@UniType NVARCHAR(MAX),
	@LanguageID BIGINT=NULL
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @CustomerID BIGINT;
EXEC [dbo].[Customer_Create_Select] @ServiceLevelID, @AccountID, @CustomerID output

DECLARE @RequestID BIGINT, @RequestNumber NVARCHAR (32);

SELECT @UniType=RIC.UniType
FROM dbo.RequestInformation R
INNER JOIN dbo.Request RIC ON R.RequestID = RIC.RequestID
WHERE R.CustomerID = @CustomerID AND RIC.IsActive=1


BEGIN
    SELECT @IsNewRequest = 1;
    DECLARE @PersonaName NVARCHAR(50), @UpdatedBy nvarchar(50), @Comments nvarchar(4000);

    SELECT @PersonaName = P.PersonaName
    FROM dbo.[User] U
    INNER JOIN dbo.Persona P ON U.PersonaID = P.PersonaID
    WHERE UserID = @UserID;

    EXEC dbo.Request_Insert @UserID, UpdatedBy, @Comments, @RequestID output, @SpeedSheetName, @UniType

    DECLARE @RequestInformationID BIGINT;
    EXEC dbo.RequestInformation_Insert @RequestID, @CustomerID, @UpdatedBy, @Comments, @LanguageID, @RequestInformationID output

    DECLARE @RequestProfileID BIGINT;
    EXEC dbo.RequestProfile_Insert @RequestID, @UpdatedBy, @Comments, @RequestProfileID output


END

SET @OutputRequestID = (SELECT @RequestID);

COMMIT TRAN
