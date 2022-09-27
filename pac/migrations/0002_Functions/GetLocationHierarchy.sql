CREATE OR ALTER FUNCTION dbo.GetLocationHierarchy
(
	@RequestSectionLanePointTypeName NVARCHAR(50)
)

RETURNS INT
AS
BEGIN
	DECLARE @LocationHierarchy INT;

	SELECT @LocationHierarchy = (SELECT DISTINCT LocationHierarchy
		FROM dbo.RequestSectionLanePointType
		WHERE RequestSectionLanePointTypeName = @RequestSectionLanePointTypeName)

	RETURN @LocationHierarchy
END

