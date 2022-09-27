CREATE OR ALTER PROCEDURE [dbo].[Request_Insert]
	@InitiatedBy BIGINT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL,
	@RequestID BIGINT output,
    @SpeedSheetName NVARCHAR(MAX)= NULL,
    @UniType NVARCHAR(MAX) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @CreatorPersona VARCHAR(100);
SELECT @CreatorPersona = personaName FROM dbo.[User] u
    INNER JOIN dbo.Persona p ON p.PersonaID = u.PersonaID
    WHERE userID = @InitiatedBy;

DECLARE @Request table
(
    [RequestID]          BIGINT        NOT NULL,
	[RequestCode]        NVARCHAR (32) NOT NULL,
	[InitiatedOn]                DATETIME2 (7)   NOT NULL,
    [InitiatedBy]                BIGINT   NOT NULL,
	[SubmittedOn]                DATETIME2 (7) NULL,
    [SubmittedBy]                BIGINT   NULL,
	[RequestOwner]    BIGINT    NOT NULL,
	[IsValidData]	BIT NOT NULL,
	[IsReview] BIT NOT NULL,
    [SpeedsheetName] [NVARCHAR](MAX) NULL,
	[UniType] [NVARCHAR](MAX) NULL,
	[RequestStatusTypeID] BIGINT NOT NULL,
	[CurrentEditorID] BIGINT NULL,
	[SalesRepresentativeID] BIGINT NULL,
	[PricingAnalystID] BIGINT NULL,
    [RequestMajorVersion] INT NOT NULL,
    [NewLanesOnly] BIT NOT NULL
)

BEGIN TRAN
INSERT INTO [dbo].[Request]
(
    [RequestCode],
	[InitiatedOn],
    [InitiatedBy],
	[SubmittedOn],
    [SubmittedBy],
	[RequestOwner],
	[IsValidData],
	[IsReview],
	[IsActive],
	[IsInactiveViewable],
    [SpeedsheetName],
    [UniType],
    [RequestStatusTypeID],
    [CurrentEditorID] ,
    [SalesRepresentativeID] ,
    [PricingAnalystID],
    [RequestMajorVersion],
    [NewLanesOnly]
)
OUTPUT INSERTED.[RequestID],
	CONCAT(LEFT(DATEPART(yy, GETUTCDATE()), 2), REPLICATE('0', 7 - LEN(INSERTED.[RequestID]%10000000)), INSERTED.[RequestID]%10000000),
	INSERTED.[InitiatedOn],
    INSERTED.[InitiatedBy],
	INSERTED.[SubmittedOn],
    INSERTED.[SubmittedBy],
	INSERTED.[RequestOwner],
	INSERTED.[IsValidData],
	INSERTED.[IsReview],
    INSERTED. [SpeedsheetName],
    INSERTED.[UniType],
    INSERTED.[RequestStatusTypeID],
    INSERTED.[CurrentEditorID] ,
    INSERTED.[SalesRepresentativeID] ,
    INSERTED.[PricingAnalystID],
    INSERTED.[RequestMajorVersion],
    INSERTED.[NewLanesOnly]
INTO @Request
(
	[RequestID],
	[RequestCode],
	[InitiatedOn],
    [InitiatedBy],
	[SubmittedOn],
    [SubmittedBy],
	[RequestOwner],
	[IsValidData],
	[IsReview],
    [SpeedsheetName],
    [UniType],
    [RequestStatusTypeID],
    [CurrentEditorID] ,
    [SalesRepresentativeID] ,
    [PricingAnalystID],
    [RequestMajorVersion],
    [NewLanesOnly]
)
VALUES
(
    REPLACE(NEWID(), '-', ''),
	GETUTCDATE(),
    @InitiatedBy,
    GETUTCDATE(),
    @InitiatedBy,
	@InitiatedBy,
	1,
	1,
    1,
    1,
    @SpeedSheetName,
    @UniType,
    1,
    @InitiatedBy,
    CASE WHEN @CreatorPersona = 'Sales Representative' THEN @InitiatedBy ELSE NULL END,
    CASE WHEN @CreatorPersona = 'Pricing Analyst' THEN @InitiatedBy ELSE NULL END,
    1,
    0
)

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT

UPDATE dbo.Request
SET RequestCode = A.RequestCode
FROM @Request A
WHERE dbo.Request.RequestID = A.RequestID


INSERT INTO [dbo].[Request_History]
(
	[RequestID],
	[RequestCode],
	[InitiatedOn],
    [InitiatedByVersionID],
	[SubmittedOn],
    [SubmittedByVersionID],
	[IsValidData],
	[IsReview],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments],
	[RequestStatusTypeVersionID],
    [CurrentEditorVersionID] ,
    [SalesRepresentativeVersionID] ,
    [PricingAnalystVersionID],
    [RequestMajorVersion],
    [NewLanesOnly]
)
SELECT R.[RequestID],
	R.[RequestCode],
	R.[InitiatedOn],
    UH.[UserVersionID],
	NULL,
    NULL,
	R.[IsValidData],
	R.[IsReview],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments,
	 (select RequestStatusTypeVersionID from dbo.RequestStatusType_history WHERE RequestStatusTypeID = 1 AND IsLatestVersion = 1),
     @InitiatedBy,
     CASE WHEN @CreatorPersona = 'Sales Representative' THEN
        (select UserVersionID from dbo.User_history WHERE UserID = @InitiatedBy  AND IsLatestVersion = 1)
     ELSE NULL END,
     CASE WHEN @CreatorPersona = 'Pricing Analyst' THEN
        (select UserVersionID from dbo.User_history WHERE UserID = @InitiatedBy  AND IsLatestVersion = 1)
     ELSE NULL END,
     R.RequestMajorVersion,
     R.NewLanesOnly
FROM @Request R
INNER JOIN dbo.User_History UH ON R.InitiatedBy = UH.UserID AND UH.IsLatestVersion = 1

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT

SELECT @RequestID = R.RequestID
FROM @Request R
WHERE R.InitiatedBy = @InitiatedBy

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
