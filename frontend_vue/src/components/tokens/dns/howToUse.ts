export const howToUse = [
  'Include in a PTR entry for dark IP space of your internal network. Quick way to determine if someone is walking your internal DNS without configuring DNS logging and monitoring.',
  'Leave in a .bash_history, or .ssh/config, or ~/servers.txt',
  'Use as a extremely simple bridge between a detection and notification action. Many possibilities, here`s one that tails a logfile and triggers the token when someone logs in: <pre>tail -f /var/log/auth.log | awk `/Accepted publickey for/ { system("host k5198sfh3cw64rhdpm29oo4ga.canarytokens.com") }`</pre>',
  'Use as the domain part of an email address.',
];
