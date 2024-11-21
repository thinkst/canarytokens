import type { NetworkFolderDataType } from './types';

export default function generateNetworkFoldertoken(NetworkFolder: NetworkFolderDataType) {
  const usageDescription = `cmdkey /add:${NetworkFolder.webdav_server} /user:user /pass:${NetworkFolder.webdav_password}
NET USE * \\\\${NetworkFolder.webdav_server}@SSL\\DavWWWRoot /persistent:yes`
    return usageDescription;
}
