IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[GetRequestSectionLaneDefaultCost]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[GetRequestSectionLaneDefaultCost]
GO

CREATE FUNCTION dbo.GetRequestSectionLaneDefaultCost
(
	@RequestSectionID BIGINT
)

RETURNS NVARCHAR(MAX)
AS
BEGIN

	DECLARE @Cost NVARCHAR(MAX);

	DECLARE @WeightBreak NVARCHAR(MAX);

	SELECT @WeightBreak = WeightBreak
	FROM dbo.RequestSection
	WHERE RequestSectionID = @RequestSectionID

	SELECT @Cost = '{}'
	return @Cost
END
GO

