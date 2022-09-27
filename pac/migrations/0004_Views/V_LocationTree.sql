CREATE OR ALTER VIEW dbo.V_LocationTree AS
SELECT c.CountryID, null RegionID, null ProvinceID, null BasingPointID, null ServicePointID, null PostalCodeID, null TerminalID,
    c.CountryID ID, c.CountryCode Code, c.CountryName Name, pt.PointTypeID, pt.PointTypeName, pt.PointTypeOrderID
    FROM dbo.Country c INNER JOIN dbo.PointType pt ON pt.PointTypeID = 1
    WHERE c.IsActive = 1
UNION ALL
SELECT c.CountryID, r.RegionID RegionID, null ProvinceID, null BasingPointID, null ServicePointID, null PostalCodeID, null TerminalID,
    r.RegionID ID, r.RegionCode Code, r.RegionName Name, pt.PointTypeID, pt.PointTypeName, pt.PointTypeOrderID
    FROM dbo.Region r
    INNER JOIN dbo.Country c ON c.CountryID = r.CountryID
    INNER JOIN dbo.PointType pt ON pt.PointTypeID = 2
    WHERE r.IsActive = 1 AND c.IsActive = 1
UNION ALL
SELECT c.CountryID, r.RegionID RegionID, p.ProvinceID ProvinceID, null BasingPointID, null ServicePointID, null PostalCodeID, null TerminalID,
    p.ProvinceID ID, p.ProvinceCode Code, p.ProvinceName Name, pt.PointTypeID, pt.PointTypeName, pt.PointTypeOrderID
    FROM dbo.Province p
    INNER JOIN dbo.Region r ON p.RegionID = r.RegionID
    INNER JOIN dbo.Country c ON c.CountryID = r.CountryID
    INNER JOIN dbo.PointType pt ON pt.PointTypeID = 3
    WHERE p.IsActive = 1 AND r.IsActive = 1 AND c.IsActive = 1
UNION ALL
SELECT c.CountryID, r.RegionID RegionID, p.ProvinceID ProvinceID, bp.BasingPointID BasingPointID, null ServicePointID, null PostalCodeID, bp.DefaultTerminalID TerminalID,
    bp.BasingPointID ID, bp.BasingPointCode Code, bp.BasingPointName Name, pt.PointTypeID, pt.PointTypeName, pt.PointTypeOrderID
    FROM dbo.BasingPoint bp
    INNER JOIN dbo.Province p ON bp.ProvinceID = p.ProvinceID
    INNER JOIN dbo.Region r ON p.RegionID = r.RegionID
    INNER JOIN dbo.Country c ON c.CountryID = r.CountryID
    INNER JOIN dbo.PointType pt ON pt.PointTypeID = 5
    WHERE bp.IsActive = 1 AND p.IsActive = 1 AND r.IsActive = 1 AND c.IsActive = 1
UNION ALL
SELECT c.CountryID, r.RegionID RegionID, p.ProvinceID ProvinceID, bp.BasingPointID BasingPointID, sp.ServicePointID ServicePointID, null PostalCodeID, bp.DefaultTerminalID TerminalID,
    sp.ServicePointID ID, sp.ServicePointCode Code, sp.ServicePointName Name, pt.PointTypeID, pt.PointTypeName, pt.PointTypeOrderID
    FROM dbo.ServicePoint sp
    INNER JOIN dbo.BasingPoint bp ON sp.BasingPointID = bp.BasingPointID
    INNER JOIN dbo.Province p ON bp.ProvinceID = p.ProvinceID
    INNER JOIN dbo.Region r ON p.RegionID = r.RegionID
    INNER JOIN dbo.Country c ON c.CountryID = r.CountryID
    INNER JOIN dbo.PointType pt ON pt.PointTypeID = 6
    WHERE sp.IsActive = 1 AND bp.IsActive = 1 AND p.IsActive = 1 AND r.IsActive = 1 AND c.IsActive = 1
UNION ALL
SELECT c.CountryID, r.RegionID RegionID, p.ProvinceID ProvinceID, bp.BasingPointID BasingPointID, null ServicePointID, pc.PostalCodeID PostalCodeID, bp.DefaultTerminalID TerminalID,
    pc.PostalCodeID ID, pc.PostalCodeName Code, pc.PostalCodeName Name, pt.PointTypeID, pt.PointTypeName, pt.PointTypeOrderID
    FROM dbo.PostalCode pc
    INNER JOIN dbo.BasingPoint bp ON pc.BasingPointID = bp.BasingPointID
    INNER JOIN dbo.Province p ON bp.ProvinceID = p.ProvinceID
    INNER JOIN dbo.Region r ON p.RegionID = r.RegionID
    INNER JOIN dbo.Country c ON c.CountryID = r.CountryID
    INNER JOIN dbo.PointType pt ON pt.PointTypeID = 7
    WHERE pc.IsActive = 1 AND bp.IsActive = 1 AND p.IsActive = 1 AND r.IsActive = 1 AND c.IsActive = 1
UNION ALL
SELECT c.CountryID, r.RegionID RegionID, p.ProvinceID ProvinceID, bp.BasingPointID BasingPointID, null ServicePointID, null PostalCodeID, t.TerminalID TerminalID,
    t.TerminalID ID, t.TerminalCode Code, t.TerminalName Name, pt.PointTypeID, pt.PointTypeName, pt.PointTypeOrderID
    FROM dbo.Terminal t
    INNER JOIN dbo.BasingPoint bp ON bp.BasingPointID = t.BasingPointID
    INNER JOIN dbo.Province p ON bp.ProvinceID = p.ProvinceID
    INNER JOIN dbo.Region r ON p.RegionID = r.RegionID
    INNER JOIN dbo.Country c ON c.CountryID = r.CountryID
    INNER JOIN dbo.PointType pt ON pt.PointTypeID = 4
    WHERE t.IsActive = 1 AND bp.IsActive = 1 AND p.IsActive = 1 AND r.IsActive = 1 AND c.IsActive = 1
;