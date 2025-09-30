export const howToUse = [
  'Include the snippet in a PTR entry for dark IP space of your internal network. It\'s a quick way to determine if someone is walking your internal DNS without configuring DNS logging and monitoring.',
  'Leave it in <code>.bash_history</code>, or <code>.ssh/config</code>, or <code>~/servers.txt</code>',
  'Use the snippet as an extremely simple bridge between a detection and notification action. Here\'s an example that tails a logfile and triggers the token when someone logs in: <code>tail -f /var/log/auth.log | awk `/Accepted publickey for/ { system("host k5198sfh3cw64rhdpm29oo4ga.canarytokens.com") }`</code>',
  'Use the snippet as the domain part of an email address.',
];
