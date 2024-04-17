export default function generateSVNToken(hostname: string) {
  return `svn propset svn:externals "extras http://${hostname}" .`;
}
