CREATE OR ALTER FUNCTION dbo.GetRequestSectionLaneDefaultCost
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

