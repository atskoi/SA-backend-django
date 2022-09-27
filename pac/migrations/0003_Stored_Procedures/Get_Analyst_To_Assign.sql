CREATE OR ALTER PROCEDURE [dbo].[Get_Analyst_To_Assign]
	@UserType VARCHAR(50),
	@RequestID BIGINT
AS

SET NOCOUNT ON;

DECLARE @LastPricingID BIGINT;
DECLARE @CurrentUserID BIGINT;
DECLARE @CountUsers INT;
DECLARE @NextID INT;
DECLARE @ServiceLevelID BIGINT;
DECLARE @UserIDs TABLE(
    UserID BIGINT,
    RowNum INT
)

select @ServiceLevelID = c.ServiceLevelID,
    @CurrentUserID = CASE WHEN @UserType = 'Pricing Analyst' THEN r.PricingAnalystID
    WHEN @UserType = 'Sales Rep' THEN r.SalesRepresentativeID
    ELSE null END
from dbo.Request r
INNER JOIN dbo.RequestInformation ri ON ri.RequestNumber = r.RequestNumber
INNER JOIN dbo.Customer c ON c.CustomerID = ri.CustomerID
WHERE r.RequestID = @RequestID;

INSERT INTO @UserIDs
select u.UserID, ROW_NUMBER() OVER(ORDER BY u.UserID ASC)
from dbo.[User] u
INNER JOIN dbo.UserServiceLevel usl ON usl.UserID = u.UserID
INNER JOIN dbo.Persona p ON p.PersonaID = u.PersonaID
WHERE usl.ServiceLevelID = @ServiceLevelID AND p.PersonaName = @UserType
ORDER BY u.UserID;

IF @CurrentUserID IS NOT NULL
    SELECT @CurrentUserID NextUser;
ELSE
    BEGIN
    SELECT top(1) @LastPricingID = r.PricingAnalystID
    from dbo.Request r
    INNER JOIN dbo.RequestInformation ri ON ri.RequestNumber = r.RequestNumber
    INNER JOIN dbo.Customer c ON c.CustomerID = ri.CustomerID
    WHERE r.PricingAssigned IS NOT NULL AND c.ServiceLevelID = @ServiceLevelID
    ORDER BY r.PricingAssigned DESC;

    SELECT @CountUsers = count(*) from @UserIDs;
    SELECT @NextID = RowNum FROM @UserIDs
        WHERE (UserID = @LastPricingID OR (@LastPricingID IS NULL AND RowNum = 1));

    IF @NextID = @CountUsers
        SELECT UserID NextUser FROM @UserIDs WHERE RowNum = 1;
    ELSE
        SELECT UserID NextUser FROM @UserIDs WHERE RowNum = @NextID;
    END
