export const howToUse = [
  'Include in a PTR entry for dark IP space of your internal network. Quick way to determine if someone is walking your internal DNS without configuring DNS logging and monitoring.',
  'Leave in a <code>.bash_history</code>, or  <code>.ssh/config</code>, or <code>~/servers.txt</code>',
  'Use as a extremely simple bridge between a detection and notification action. Many possibilities, here`s one that tails a logfile and triggers the token when someone logs in: <code>tail -f /var/log/auth.log | awk `/Accepted publickey for/ { system("host k5198sfh3cw64rhdpm29oo4ga.canarytokens.com") }`</code>',
  'Use as the domain part of an email address.',
];
