import type { NetworkFolderDataType } from './types';

export default function generateNetworkFoldertoken(NetworkFolder: NetworkFolderDataType) {
  const usageDescription = `
      Host: ${NetworkFolder.webdav_server}
      Username: <AnyUsernameIsFine>
      Password: ${NetworkFolder.webdav_password}`
  return usageDescription;
}
