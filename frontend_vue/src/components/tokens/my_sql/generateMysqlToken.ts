export default function generateMysqlToken(
  hostname: string | null,
  token: string,
  encoded: boolean
) {
  const decodedCode = `SET @bb = CONCAT(\"CHANGE REPLICATION SOURCE TO SOURCE_PASSWORD='my-secret-pw', SOURCE_RETRY_COUNT=1, SOURCE_PORT=3306, SOURCE_HOST='${hostname}', SOURCE_SSL=0, SOURCE_USER='${token}\", @@lc_time_names, @@hostname, \"';\")`;
  const encodedCode = btoa(
    `SET @bb = CONCAT(\"CHANGE REPLICATION SOURCE TO SOURCE_PASSWORD='my-secret-pw', SOURCE_RETRY_COUNT=1, SOURCE_PORT=3306, SOURCE_HOST='${hostname}', SOURCE_SSL=0, SOURCE_USER='${token}\", @@lc_time_names, @@hostname, \"';\"`
  );
  const code = encoded
    ? `SET @b = '${encodedCode}';
SET @s2 = FROM_BASE64(@b);
PREPARE stmt1 FROM @s2;
EXECUTE stmt1;
PREPARE stmt2 FROM @bb;
EXECUTE stmt2;
START REPLICA;`
    : `${decodedCode};
PREPARE stmt FROM @bb;
EXECUTE stmt;
START REPLICA;`;
  return code;
}
