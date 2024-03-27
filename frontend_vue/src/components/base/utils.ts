export function convertBytes(
  // gracefully copied from https://gist.github.com/lanqy/5193417?permalink_comment_id=4755323#gistcomment-4755323
  bytes: number
): string {
  const decimals = 2;
  const base = 1000;
  const units = ['Bytes', 'KB', 'MB', 'GB'];

  const i = Math.floor(Math.log(bytes) / Math.log(base));

  return `${(bytes / Math.pow(base, i)).toFixed(decimals)} ${units[i]}`;
}
