CREATE OR ALTER PROCEDURE [dbo].[RequestProfile_Insert]
	@RequestID        BIGINT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL,
	@RequestProfileID NVARCHAR (32) output
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @RequestProfile table 
( 
    [RequestProfileID]          BIGINT        NOT NULL,
    [RequestID]       BIGINT NOT NULL,
	[IsValidData]	BIT NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[RequestProfile]
(
	[RequestID],
	[IsValidData],
	[IsActive],
	[IsInactiveViewable],
	[ClassControls],
	[Competitors],
	[ShippingControls],
	[Shipments],
	[FreightElements]
)
OUTPUT INSERTED.[RequestProfileID],
    INSERTED.[RequestID],
	INSERTED.[IsValidData]
INTO @RequestProfile
(
	[RequestProfileID],
	[RequestID],
	[IsValidData]
)
VALUES
(
    @RequestID,
	0,
	1,
	1,
	'[]',
	'[]',
	'[]',
	'[]',
	'[]'
)

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[RequestProfile_History]
(
	[RequestProfileID],
    [RequestVersionID],
	[IsValidData],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments],
	[ClassControls],
	[Competitors],
	[ShippingControls],
	[Shipments],
	[FreightElements]
)
SELECT R.[RequestProfileID],
    rh.[RequestVersionID],
	R.[IsValidData],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments,
	 '[]',
	'[]',
	'[]',
	'[]',
	'[]'
FROM @RequestProfile R
    INNER JOIN dbo.Request_History rh ON rh.RequestID = @RequestID AND rh.IsLatestVersion = 1

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT 

SELECT @RequestProfileID = R.RequestProfileID
FROM @RequestProfile R
WHERE R.RequestID = @RequestID

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0)

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

IF (@ROWCOUNT1 <> 1) OR (@ROWCOUNT2 <> 1)
	
	BEGIN
	ROLLBACK TRAN
	IF (@ROWCOUNT1 <> 1)
		RAISERROR('%d Records Affected by Insert Procedure!', 16, 1, @ROWCOUNT1);
	IF (@ROWCOUNT2 <> 1)
		RAISERROR('%d Records Affected by Insert Procedure!', 16, 1, @ROWCOUNT2);
	RETURN 0
	END

COMMIT TRAN
RETURN 1

