CREATE OR ALTER FUNCTION dbo.RequestSectionLane_Modify_Rate
(
	@Cost DECIMAL(19,6),
	@Operation NVARCHAR(1),
	@Multiplier DECIMAL(19,6)
)

RETURNS NVARCHAR(MAX)
AS
BEGIN

	DECLARE @NewCost DECIMAL(19,6);

	SELECT @NewCost = CASE 
	WHEN @Operation = '+' THEN @Cost + @Multiplier
	WHEN @Operation = '-' THEN @Cost - @Multiplier
	WHEN @Operation = '*' THEN @Cost * @Multiplier
	WHEN @Operation = '/' THEN @Cost / @Multiplier
	WHEN @Operation = '=' THEN @Multiplier
	END

	RETURN @NewCost

END

