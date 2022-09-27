SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE OR ALTER   PROCEDURE [dbo].[Audit_Record]
	@TableName NVARCHAR(200),
    @PrimaryKeyValue BIGINT,
	@UpdatedBy nvarchar(50) = NULL
AS

SET NOCOUNT ON;

DECLARE @PrimaryKeyName nvarchar(max);
DECLARE @RecordFound BIGINT;
DECLARE @SQLString NVARCHAR(max);
DECLARE @ParamDef NVARCHAR(500);

BEGIN TRAN

    SELECT @PrimaryKeyName = column_name
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS TC
    INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KCU
        ON TC.CONSTRAINT_TYPE = 'PRIMARY KEY'
        AND TC.CONSTRAINT_NAME = KCU.CONSTRAINT_NAME
        AND KCU.table_name=@TableName;

	SET @SQLString = N'SELECT @found = ' + @PrimaryKeyName + ' FROM ' + @TableName + ' WHERE ' + @PrimaryKeyName + ' = ' + CAST(@PrimaryKeyValue AS VARCHAR(100));
    SET @ParamDef = N'@found BIGINT OUTPUT';

    EXECUTE sp_executesql @SQLString, @ParamDef, @found = @RecordFound OUTPUT;

    DECLARE @FK_COLUMNS table (
	[row_id] INT IDENTITY(1, 1) primary key,
	[primary_table] [nvarchar](max) NOT NULL,
	[primary_column_name] [nvarchar](max) NOT NULL,
	[primary_column_version_name] [nvarchar](max) NOT NULL,
    [fk_table] [nvarchar](max) NOT NULL,
	[fk_column_name] [nvarchar](max) NOT NULL,
	[fk_column_version_name] [nvarchar](max) NOT NULL
    );
	DECLARE @MAIN_COLUMNS table (
	[primary_column_name] [nvarchar](max) NOT NULL
    );
   INSERT INTO @FK_COLUMNS ([primary_table], [primary_column_name], [primary_column_version_name],
   [fk_table], [fk_column_name], [fk_column_version_name] )
    SELECT schema_name(p.schema_id) + '.' + p.name as primary_table,
        fk_col.name as primary_column_name,
        CASE WHEN SUBSTRING(fk_col.name, LEN(fk_col.name) - 1, 2) = 'ID' THEN
            SUBSTRING(fk_col.name, 1, LEN(fk_col.name) - 2) + 'VersionID'
        ELSE fk_col.name + 'VersionID' END as primary_column_version_name,
        schema_name(ft.schema_id) + '.' + ft.name as fk_table,
        pk_col.name as fk_column_name,
		SUBSTRING(pk_col.name, 1, LEN(pk_col.name) - 2) + 'VersionID' as fk_column_version_name
    FROM sys.foreign_keys fk
    inner join sys.tables p on p.object_id = fk.parent_object_id
        inner join sys.tables ft on ft.object_id = fk.referenced_object_id
        inner join sys.foreign_key_columns fk_cols on fk_cols.constraint_object_id = fk.object_id
        inner join sys.columns fk_col on fk_col.column_id = fk_cols.parent_column_id
            and fk_col.object_id = p.object_id
        inner join sys.columns pk_col on pk_col.column_id = fk_cols.referenced_column_id
            and pk_col.object_id = ft.object_id
    where p.name = @TableName AND ft.schema_id = 1;

    INSERT INTO @MAIN_COLUMNS ([primary_column_name])
	SELECT col.name from sys.tables t
	inner join sys.columns col on col.object_id = t.object_id
	where t.name = @TableName AND t.schema_id = 1 AND col.name NOT IN (SELECT primary_column_name FROM @FK_COLUMNS);

    DECLARE @AuditColumns NVARCHAR(max);
	DECLARE @AuditValues NVARCHAR(max);
	DECLARE @FKTemplate NVARCHAR(max);
	-- take the flat values that are mapped directly to _History first
	SELECT @AuditColumns =STRING_AGG(primary_column_name, ',')  FROM @MAIN_COLUMNS;
	SELECT @AuditValues =STRING_AGG(primary_column_name, ',')  FROM @MAIN_COLUMNS;

	DECLARE @Counter INT = 1;
	DECLARE @NumRows INT;
	SELECT @NumRows = COUNT(*) FROM @FK_COLUMNS;
	WHILE @Counter <= @NumRows
	BEGIN -- loop over each FK value and derive the versioned value to insert
		DECLARE @CurTable NVARCHAR(100), @CurCol NVARCHAR(100), @CurVersionCol NVARCHAR(100),
			@CurFKTable NVARCHAR(100), @CurFK NVARCHAR(100), @CurFKVersionCol NVARCHAR(100);
		SELECT @CurTable = primary_table, @CurCol = primary_column_name, @CurVersionCol = primary_column_version_name,
			@CurFKTable = fk_table, @CurFK = fk_column_name, @CurFKVersionCol = fk_column_version_name
			FROM @FK_COLUMNS WHERE row_id = @Counter;
		SET @AuditColumns = @AuditColumns + ',' + @CurVersionCol; -- eg: CustomerVersionID

		DECLARE @CurVal NVARCHAR(max) = NULL;
		SET @FKTemplate = 'SELECT @found = ISNULL( (SELECT h1.[' + @CurFKVersionCol + '] FROM ' + @CurFKTable +'_History h1
		WHERE h1.' + @CurFK + ' = (SELECT ' + @CurCol+ ' FROM dbo.[' + @TableName +'] WHERE '
            + @PrimaryKeyName + ' = ' + CAST(@PrimaryKeyValue as VARCHAR) + ') AND h1.IsLatestVersion = 1),
            (SELECT ' + @CurCol + ' FROM ' + @TableName + ' WHERE ' + @PrimaryKeyName + ' = ' + CAST(@PrimaryKeyValue as VARCHAR) + ') ) ';
		SET @ParamDef = N' @found BIGINT OUTPUT';
    	EXECUTE sp_executesql @FKTemplate, @ParamDef, @found = @CurVal OUTPUT;

		IF @CurVal IS NULL
			SET @AuditValues = @AuditValues + ', NULL';
		ELSE
			SET @AuditValues = @AuditValues + ',' + CAST(@CurVal as VARCHAR);
		SET @Counter = @Counter + 1;
	END

	-- compose the final Audit insert statement
	DECLARE @LatestID bigint;
    DECLARE @LatestNum bigint;
	DECLARE @LatestTemplate NVARCHAR(max);
	DECLARE @AuditTemplate NVARCHAR(max);

	SET @LatestTemplate =  'SELECT @found = ' + SUBSTRING(@PrimaryKeyName, 0, LEN(@PrimaryKeyName) -1) + 'VersionID
		FROM dbo.['  + @TableName +'_History] WHERE ' + @PrimaryKeyName +' = '  + CAST(@PrimaryKeyValue as VARCHAR) +' and IsLatestVersion = 1';
	EXECUTE sp_executesql @LatestTemplate, @ParamDef, @found = @LatestID OUTPUT;
    SET @LatestTemplate = 'SELECT @found =ISNULL(
    	(SELECT VersionNum FROM dbo.['  + @TableName +'_History] WHERE ' + @PrimaryKeyName +' = '  + CAST(@PrimaryKeyValue as VARCHAR) +' and
        VersionNum = (SELECT MAX(VersionNum) FROM dbo.['  + @TableName +'_History] WHERE ' + @PrimaryKeyName +' = '  + CAST(@PrimaryKeyValue as VARCHAR) + ')) , 0)';
	EXECUTE sp_executesql @LatestTemplate, @ParamDef, @found = @LatestNum OUTPUT;
	-- mark the previous latest as not the latest
	SET @LatestTemplate = 'UPDATE dbo.['  + @TableName +'_History] set IsLatestVersion = 0 WHERE '  + @TableName +'VersionID = ' + CAST(@LatestID AS VARCHAR) + ' ;';
	EXECUTE sp_executesql @LatestTemplate;

	SET @AuditTemplate = 'INSERT INTO dbo.['  + @TableName +'_History]
            (' + @AuditColumns + ',
                VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments)
            SELECT
                ' + @AuditValues + ',
                (' + CAST(@LatestNum as VARCHAR) +' + 1) VersionNum,
                1 IsLatestVersion,
                GETDATE() UpdatedOn,
                ''' + @UpdatedBy + ''' UpdatedBy,
                1 BaseVersion,
                ''Row updated'' Comments
             FROM dbo.['+ @TableName + '] p WHERE ' + @PrimaryKeyName +' = '  + CAST(@PrimaryKeyValue as VARCHAR) + ' ;';

    EXECUTE sp_executesql @AuditTemplate;
    COMMIT TRAN
    RETURN 1
GO
