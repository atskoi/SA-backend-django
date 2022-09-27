CREATE OR ALTER PROCEDURE [dbo].[Fill_Audit_Table]
	@TableName NVARCHAR(200)
AS
SET ANSI_NULLS ON
SET QUOTED_IDENTIFIER ON
SET NOCOUNT ON;
BEGIN
    DECLARE @UpdatedBy NVARCHAR(50) = 'System Audit';
    DECLARE @Comment NVARCHAR(100) = 'Initial Audit Record';;
    DECLARE @PrimaryKeyName VARCHAR(50);
    DECLARE @PrimaryID BIGINT;
    DECLARE @SQLString NVARCHAR(2000);
    DECLARE @ParamDef NVARCHAR(200);
    DECLARE @BatchSize VARCHAR(20) = '1000';


    SELECT @PrimaryKeyName = column_name
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS TC
    INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KCU
        ON TC.CONSTRAINT_TYPE = 'PRIMARY KEY'
        AND TC.CONSTRAINT_NAME = KCU.CONSTRAINT_NAME
        AND KCU.table_name=@TableName;

    DECLARE @RowsRemaining INT = 1;
    WHILE @RowsRemaining > 0 BEGIN
        BEGIN TRANSACTION;
        CREATE TABLE #AuditIDs (
            PrimaryID BIGINT
        );
        SET @SQLString = N'SELECT TOP(' + @BatchSize + ') ' + @PrimaryKeyName + ' FROM dbo.[' + @TableName
        + '] p WHERE NOT EXISTS (SELECT * FROM dbo.[' + @TableName + '_History] ph WHERE ph.'
        + @PrimaryKeyName + ' = p.' + @PrimaryKeyName + ' )';

        INSERT INTO #AuditIDs
        EXECUTE sp_executesql @SQLString; --, @ParamDef, @dest = @AuditIDs OUTPUT;

        SELECT @RowsRemaining = COUNT(*) FROM #AuditIDs;

        declare cur CURSOR LOCAL FOR SELECT PrimaryID FROM #AuditIds;
        open cur;

        FETCH NEXT FROM cur into @PrimaryID;

        while @@FETCH_STATUS = 0 BEGIN
            -- add the missing audit record for each orphaned PrimaryID
            EXEC dbo.[Audit_Record] @TableName = @TableName, @PrimaryKeyValue = @PrimaryID, @UpdatedBy = @UpdatedBy;
            FETCH NEXT FROM cur into @PrimaryID;
        END

        close cur;
        deallocate cur;
        DROP TABLE #AuditIDs;
        DECLARE @msg NVARCHAR(500);
        DECLARE @Unauditied INT;
        SET @SQLString = N'SELECT COUNT(1) ' + @PrimaryKeyName + ' FROM dbo.[' + @TableName
        + '] p WHERE NOT EXISTS (SELECT * FROM dbo.[' + @TableName + '_History] ph WHERE ph.'
        + @PrimaryKeyName + ' = p.' + @PrimaryKeyName + ' )';
        SET @ParamDef = N'@Counter BIGINT OUTPUT';
        EXECUTE sp_executesql @SQLString, @ParamDef, @Counter = @Unauditied OUTPUT;
        SET @msg = 'audited rows: ' + CAST(@RowsRemaining AS NVARCHAR) + ' out of ' + CAST(@Unauditied as NVARCHAR);
        RAISERROR(@msg, 0, 1) WITH NOWAIT;
        COMMIT;
    END;
END