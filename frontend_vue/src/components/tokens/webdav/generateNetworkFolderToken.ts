import type { NetworkFolderDataType } from './types';

export default function generateNetworkFoldertoken(NetworkFolder: NetworkFolderDataType) {
  const domain = NetworkFolder.webdav_server?.split("/")[2];
  const usageDescription = `# Run the next line once to save the credentials:
cmdkey /generic:${domain} /user:user /pass:${NetworkFolder.webdav_password}

# On each boot run the line below in a startup script:
net use * ${NetworkFolder.webdav_server} /savecred`
    return usageDescription;
}
