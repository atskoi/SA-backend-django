DECLARE @CountConstraint INT = 0;
  SELECT @CountConstraint = COUNT(1) FROM sys.default_constraints dc
  INNER JOIN sys.objects o on o.object_id = dc.object_id
  WHERE o.name = 'DF_SpotQuoteMargin_UpdatedOn';

  
if @CountConstraint <= 0 BEGIN
    ALTER TABLE SpotQuoteMargin ADD CONSTRAINT DF_SpotQuoteMargin_UpdatedOn DEFAULT GETDATE() FOR UpdatedOn;
END
