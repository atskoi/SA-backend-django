CREATE OR ALTER PROCEDURE [dbo].[Request_By_Account_Select] @UserID BIGINT,
                                                   @ServiceLevelID BIGINT,
                                                   @AccountID BIGINT = NULL,
                                                   @SpeedSheetName varchar(1000)=NULL,
                                                   @UniType NVARCHAR(MAX)=NULL,
                                                   @LanguageName varchar(2)=NULL
AS

SET NOCOUNT ON;

DECLARE @RequestID BIGINT;
DECLARE @IsNewRequest BIT;
DECLARE @LanguageId BIGINT = (select LanguageID from Language where LanguageCode= @LanguageName)

EXEC [dbo].[Request_Create_Select] @UserID, @ServiceLevelID, @AccountID, @RequestID output,
         @IsNewRequest output, @SpeedSheetName, @UniType, @LanguageId;

EXEC [dbo].[Request_By_ID_Select] @RequestID, @IsNewRequest;


