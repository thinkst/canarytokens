import{_ as r}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-_edp5TVX.js";import{d as o,r as c,a as i,b as l,u as m}from"./index-C2GNx2pT.js";function u(e){const n=`
--create a stored proc that'll ping canarytokens
  CREATE proc ping_canarytoken
  AS
  BEGIN
      declare @username varchar(max), @base64 varchar(max), @tokendomain varchar(128), @unc varchar(128), @size int, @done int, @random varchar(3);

      --setup the variables
      set @tokendomain = '${e.hostname}';
      set @size = 128;
      set @done = 0;
      set @random = cast(round(rand()*100,0) as varchar(2));
      set @random = concat(@random, '.');
      set @username = SUSER_SNAME();

      --loop runs until the UNC path is 128 chars or less
      while @done <= 0
      begin
          --convert username into base64
          select @base64 = (SELECT
              CAST(N'' AS XML).value(
                    'xs:base64Binary(xs:hexBinary(sql:column("bin")))'
                  , 'VARCHAR(MAX)'
              )   Base64Encoding
          FROM (
              SELECT CAST(@username AS VARBINARY(MAX)) AS bin
          ) AS bin_sql_server_temp);

          --replace base64 padding as dns will choke on =
          select @base64 = replace(@base64,'=','-')

          --construct the UNC path
          select @unc = concat('\\',@base64,'.',@random,@tokendomain,'a')

          -- if too big, trim the username and try again
          if len(@unc) <= @size
              set @done = 1
          else
              --trim from the front, to keep the username and lose domain details
              select @username = substring(@username, 2, len(@username)-1)
      end
      exec master.dbo.xp_fileexist @unc;
  END

  --add a trigger if data is altered
  CREATE TRIGGER ${e.sql_trigger_name}
    ON ${e.sql_table_name}
    AFTER ${e.sql_action}
  AS
  BEGIN
  exec ping_canarytoken
  end`,a=`
--create a table-view function to query the canary hostname
  CREATE function ${e.sql_function_name}(@RAND FLOAT) returns @output table (col1 varchar(max))
  AS
  BEGIN
      declare @username varchar(max), @base64 varchar(max), @tokendomain varchar(128), @unc varchar(128), @size int, @done int, @random varchar(3);

      --setup the variables
      set @tokendomain = '${e.hostname}';
      set @size = 128;
      set @done = 0;
      set @random = cast(round(@RAND*100,0) as varchar(2));
      set @random = concat(@random, '.');
      set @username = SUSER_SNAME();

      --loop runs until the UNC path is 128 chars or less
      while @done <= 0
      begin
          --convert username into base64
          select @base64 = (SELECT
              CAST(N'' AS XML).value(
                    'xs:base64Binary(xs:hexBinary(sql:column("bin")))'
                  , 'VARCHAR(MAX)'
              )   Base64Encoding
          FROM (
              SELECT CAST(@username AS VARBINARY(MAX)) AS bin
          ) AS bin_sql_server_temp);

          --replace base64 padding as dns will choke on =
          select @base64 = replace(@base64,'=','0')

          --construct the UNC path
          select @unc = concat('\\',@base64,'.',@random,@tokendomain,'a')

          -- if too big, trim the username and try again
          if len(@unc) <= @size
              set @done = 1
          else
              --trim from the front, to keep the username and lose domain details
              select @username = substring(@username, 2, len(@username)-1)
      end
      exec master.dbo.xp_dirtree @unc-- WITH RESULT SETS (([result] varchar(max)));
          return
  END

  --create a view that calls the function
  alter view ${e.sql_server_view_name} as select * from master.dbo.<span class="${e.sql_function_name}(rand());

  --change permissions on ${e.sql_function_name} to SELECT for [public]
  --change permissions on ${e.sql_server_view_name} to SELECT for [public]
  --don't allow [public] to view the definitions`;return e.sql_action==="SELECT"?a:n}const b=o({__name:"TokenDisplay",props:{tokenData:{}},setup(e){const n=e,a=c({hostname:n.tokenData.hostname,sql_table_name:n.tokenData.sql_table_name,sql_trigger_name:n.tokenData.sql_trigger_name,sql_function_name:n.tokenData.sql_function_name,sql_server_view_name:n.tokenData.sql_server_view_name,sql_action:n.tokenData.sql_action}),s=u(a.value);return(d,_)=>{const t=r;return i(),l(t,{lang:"sql",label:"Microsoft Server SQL token",code:m(s),"custom-height":"10rem","show-expand-button":""},null,8,["code"])}}});export{b as _};
