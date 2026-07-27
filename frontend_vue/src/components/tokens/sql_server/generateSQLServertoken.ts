import type { SQLServerDataType } from './types';

export default function generateSQLServertoken(SQLData: SQLServerDataType) {
  const snippetIsNotSelect = `
-- Create a stored procedure that will ping canarytokens
CREATE PROC ping_canarytoken
AS
BEGIN
    DECLARE @username varchar(max), @base64 varchar(max), @tokendomain varchar(128), @unc varchar(128), @size int, @done int, @random varchar(3);

    -- Setup the variables
    SET @tokendomain = '${SQLData.hostname}';
    SET @size = 128;
    SET @done = 0;
    SET @random = cast(round(rand()*100,0) as varchar(2));
    SET @random = concat(@random, '.');
    SET @username = SUSER_SNAME();

    -- Loop runs until the UNC path is 128 chars or less
    WHILE @done <= 0
    BEGIN
        -- Convert username into base64
        SELECT @base64 = (SELECT
            CAST(N'' AS XML).value(
                'xs:base64Binary(xs:hexBinary(sql:column("bin")))'
                , 'VARCHAR(MAX)'
            )   Base64Encoding
        FROM (
            SELECT CAST(@username AS VARBINARY(MAX)) AS bin
        ) AS bin_sql_server_temp);

        -- Replace base64 padding as dns will choke on =
        SELECT @base64 = replace(@base64,'=','-')

        -- Construct the UNC path
        SELECT @unc = concat('\\\\',@base64,'.',@random,@tokendomain,'\\a')

        -- If too big, trim the username and try again
        if len(@unc) <= @size
            SET @done = 1
        else
            -- Trim from the front, to keep the username and lose domain details
            SELECT @username = substring(@username, 2, len(@username)-1)
    END
    EXEC master.dbo.xp_fileexist @unc;
END
GO

-- Add a trigger if data is altered in your table
CREATE TRIGGER ${SQLData.sql_trigger_name}
ON dbo.${SQLData.sql_table_name}
AFTER ${SQLData.sql_action}
AS
BEGIN
    EXEC dbo.ping_canarytoken
END
GO
`;

  const snippetIsSelect = `
-- Create a table-view function to query the canarytokens hostname
CREATE FUNCTION ${SQLData.sql_function_name}(@RAND FLOAT) RETURNS @output table (col1 varchar(max))
AS
BEGIN
    DECLARE @username varchar(max), @base64 varchar(max), @tokendomain varchar(128), @unc varchar(128), @size int, @done int, @random varchar(3);

    -- Setup the variables
    SET @tokendomain = '${SQLData.hostname}';
    SET @size = 128;
    SET @done = 0;
    SET @random = cast(round(@RAND*100,0) as varchar(2));
    SET @random = concat(@random, '.');
    SET @username = SUSER_SNAME();

    -- Loop runs until the UNC path is 128 chars or less
    WHILE @done <= 0
    BEGIN
        -- Convert username into base64
        SELECT @base64 = (SELECT
            CAST(N'' AS XML).value(
                'xs:base64Binary(xs:hexBinary(sql:column("bin")))'
                , 'VARCHAR(MAX)'
            )   Base64Encoding
        FROM (
            SELECT CAST(@username AS VARBINARY(MAX)) AS bin
        ) AS bin_sql_server_temp);

        -- Replace base64 padding as dns will choke on =
        SELECT @base64 = replace(@base64,'=','0')

        -- Construct the UNC path
        SELECT @unc = concat('\\\\',@base64,'.',@random,@tokendomain,'\\a')

        -- If too big, trim the username and try again
        if len(@unc) <= @size
            SET @done = 1
        else
            -- Trim from the front, to keep the username and lose domain details
            SELECT @username = substring(@username, 2, len(@username)-1)
    END
    EXEC master.dbo.xp_dirtree @unc-- WITH RESULT SETS (([result] varchar(max)));
        RETURN
END
GO

-- Alter your database view to call the above function
ALTER VIEW ${SQLData.sql_server_view_name}
AS
    SELECT * from dbo.${SQLData.sql_function_name}(rand());
GO

-- To allow database users, who only have the public database role, to run "SELECT" queries against the ${SQLData.sql_server_view_name} view:
--    Grant the public database role "SELECT" permission on the dbo.${SQLData.sql_function_name} function.
--    Grant the public database role "SELECT" permission on the ${SQLData.sql_server_view_name} view.
--    Do not grant the public database role "VIEW DEFINITION" permission on either the dbo.${SQLData.sql_function_name} function or the ${SQLData.sql_server_view_name} view.
`;

  return SQLData.sql_action === 'SELECT' ? snippetIsSelect : snippetIsNotSelect;
}
