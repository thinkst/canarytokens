// when Managing an existing MySQL token
// we generate it on the frontend
// by using 'auth code' and 'generated_hostname'
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

export default function generateManagedToken(data: ManageTokenBackendType) {
  const hostname = data.canarydrop.generated_hostname;
  const token = data.canarydrop.canarytoken._value;
  const code = `SET @bb = CONCAT(\"CHANGE MASTER TO MASTER_PASSWORD='my-secret-pw', MASTER_RETRY_COUNT=1, MASTER_PORT=3306, MASTER_HOST='${hostname}', MASTER_USER='${token}\", @@lc_time_names, @@hostname, \"';\");`;
  return code;
}
