export const howToUse = [
  'Map a Network Drive and get notified if the drive is accessed.',
  'On <strong>Windows</strong>, run these commands from cmd.exe: \
  <ul>\
    <li><code>C:\\> cmdkey /add:docvaultstorage.com /user:USERNAME_HERE /pass:PASSWORD_HERE</code></li>\
    <li><code>C:\\> NET USE * \\\\docvaultstorage.com@SSL\\DavWWWRoot /persistent:yes</code>\
  </ul>',
  'On <strong>MacOS</strong>: \
  <ul>\
    <li>Open the Finder, then type &#8984;-K to Connect to Server</li>\
    <li>Enter "https://docvaultstorage.com" as the hostname, and click Connect</li>\
    <li>Enter any username, but use the password we gave you</li>\
    <li>Optionally you can save the credentials into your Keychain if you want to remount at login. To remount at log, open System Settings -> General -> Open at Login, click the \'+\' to add a new item, navigate to the newly-mounted folder, and select it, then click Open.</li>\
  </ul>',

];
