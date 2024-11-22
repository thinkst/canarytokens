import { TOKENS_TYPE, TOKEN_CATEGORY } from '@/components/constants.ts';

export type TokenServiceType = {
  label: string;
  description: string;
  documentationLink: string;
  icon: string;
  instruction: string;
  howItWorksInstructions?: string[];
  category?: string | string[];
  keywords?: string[];
};

export type TokenServicesType = {
  [key: string]: TokenServiceType;
};

export const tokenServices: TokenServicesType = {
  [TOKENS_TYPE.WEB_BUG]: {
    label: 'Web bug',
    description: 'Get an alert when an attacker visits your URL.',
    documentationLink: 'https://docs.canarytokens.org/guide/http-token.html',
    icon: `${TOKENS_TYPE.WEB_BUG}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish',
    howItWorksInstructions: [
      'We give you a unique URL.',
      'You place it somewhere.',
      'We send you an alert if that URL is ever viewed.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: ['http', 'url'],
  },
  [TOKENS_TYPE.DNS]: {
    label: 'DNS',
    description: 'Get an alert when an attacker resolves a DNS name.',
    documentationLink: 'https://docs.canarytokens.org/guide/dns-token.html',
    icon: `${TOKENS_TYPE.DNS}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish',
    howItWorksInstructions: [
      'We give you a unique DNS name.',
      'You place it somewhere.',
      'We send you an alert if that DNS name is ever resolved.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: ['domain'],
  },
  [TOKENS_TYPE.CREDIT_CARD_V2]: {
    label: 'Credit Card',
    description: 'Get an alert when an attacker attempt to use your credit card.',
    documentationLink: 'https://docs.canarytokens.org/guide/qr-code-token.html',
    icon: `${TOKENS_TYPE.CREDIT_CARD_V2}.png`,
    instruction: 'Place it on your computer and get notified when your\'e breached:',
    howItWorksInstructions: [
      'We give you unique Credit Card details',
      'You place it somewhere.',
      'We send you an alert when that Credit Card is used.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: ['cc'],
  },
  [TOKENS_TYPE.QRCODE]: {
    label: 'QR code',
    description: 'Get an alert when an attacker follows your QR Code.',
    documentationLink: 'https://docs.canarytokens.org/guide/qr-code-token.html',
    icon: `${TOKENS_TYPE.QRCODE}.png`,
    instruction: 'Use this QR Code to token a physical location or object:',
    howItWorksInstructions: [
      'We give you a unique QR code.',
      'You place it somewhere.',
      'We send you an alert when that QR code is viewed & followed.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: ['barcode', 'mobile'],
  },
  [TOKENS_TYPE.MYSQL]: {
    label: 'MySQL',
    description: 'Get an alert when an attacker loads your MySQL dump.',
    documentationLink:
      'https://docs.canarytokens.org/guide/mysql-dump-token.html',
    icon: `${TOKENS_TYPE.MYSQL}.png`,
    instruction: '',
    howItWorksInstructions: [
      'We give you a uniquely generated MySQL dump.',
      'You place it somewhere.',
      'We send you an alert if someone loads the dumpfile into a running MySQL instance.',
    ],
    category: TOKEN_CATEGORY.DATABASE,
    keywords: ['db', 'database']
  },
  [TOKENS_TYPE.AWS_KEYS]: {
    label: 'AWS keys',
    description: 'Get an alert when an attacker uses your AWS API Key.',
    documentationLink:
      'https://docs.canarytokens.org/guide/aws-keys-token.html',
    icon: `${TOKENS_TYPE.AWS_KEYS}.png`,
    instruction:
      'Copy this credential pair to your clipboard to use as desired:',
    howItWorksInstructions: [
      'We give you a legit (defanged) AWS API Key.',
      'You place it somewhere.',
      'We send you an alert if some tries to use that key.',
    ],
    category: TOKEN_CATEGORY.CLOUD,
    keywords: ['cloud', 'api']
  },
  [TOKENS_TYPE.PWA]: {
    label: 'Fake App',
    description: 'Get an alert when someone opens a fake app on your device.',
    documentationLink: 'https://docs.canarytokens.org/guide/fake-app-token.html',
    icon: `${TOKENS_TYPE.PWA}.png`,
    instruction: 'Open the link to the app\'s page in your Native Browser (iOS: Safari, Android: Chrome) and install the app.',
    howItWorksInstructions: [
      'We give you a fake app.',
      'You install it on your phone.',
      'We send you an alert if that app is ever opened.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: ['mobile', 'pwa']
  },
  [TOKENS_TYPE.LOG4SHELL]: {
    label: 'Log4shell',
    description:
      'Get an alert when a log4j logline is vulnerable to CVE-2021-44-228.',
    documentationLink: '',
    icon: `${TOKENS_TYPE.LOG4SHELL}.png`,
    instruction:
      'The next step is to copy the log4j snippet below and test your systems for the log4shell issue.',
    howItWorksInstructions: [
      'We give you a unique log4j snippet.',
      'You place it somewhere.',
      'We send you an alert if log4j logline is consumed by a vulnerable log4j library.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: ['vulnerability']
  },
  [TOKENS_TYPE.FAST_REDIRECT]: {
    label: 'Fast redirect',
    description:
      'Get an alert when an attacker visits your URL (then redirect them).',
    documentationLink:
      'https://docs.canarytokens.org/guide/fast-redirect-token.html',
    icon: `${TOKENS_TYPE.FAST_REDIRECT}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish:',
    howItWorksInstructions: [
      'We give you a unique URL.',
      'You place it somewhere.',
      'We send you an alert if an attacker visits your URL.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: ['web', 'http', 'url']
  },
  [TOKENS_TYPE.SLOW_REDIRECT]: {
    label: 'Slow redirect',
    description:
      'Get an alert when an attacker visits your URL (then redirect them and collect more info).',
    documentationLink:
      'https://docs.canarytokens.org/guide/slow-redirect-token.html',
    icon: `${TOKENS_TYPE.SLOW_REDIRECT}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish:',
    howItWorksInstructions: [
      'We give you a unique URL.',
      'You place it somewhere.',
      'We send you an alert if an attacker visits your URL.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: ['web', 'http', 'url']
  },
  [TOKENS_TYPE.SENSITIVE_CMD]: {
    label: 'Sensitive command',
    description: 'Get an alert when a suspicious Windows command is run.',
    documentationLink:
      'https://docs.canarytokens.org/guide/sensitive-cmd-token.html',
    icon: `${TOKENS_TYPE.SENSITIVE_CMD}.png`,
    instruction: '',
    howItWorksInstructions: [
      'We give you a Windows registry file.',
      'You import the registry file.',
      'We send you an alert if an attacker runs that Windows command.',
    ],
    category: TOKEN_CATEGORY.MICROSOFT,
    keywords: ['windows', 'cmd']
  },
  [TOKENS_TYPE.WINDOWS_FAKE_FS]: {
    label: 'Windows Fake File System',
    description: 'Get an alert when an attacker accesses a file in the fake file system.',
    documentationLink:
      'https://docs.canarytokens.org/guide/TBD.html',
    icon: `${TOKENS_TYPE.WINDOWS_FAKE_FS}.png`,
    instruction: '',
    howItWorksInstructions: [
      'We give you a Powershell script.',
      'You run the script to configure the fake file system on your machine.',
      'We send you an alert if an attacker opens or copies a file.',
    ],
    category: TOKEN_CATEGORY.MICROSOFT,
    keywords: ['windows', 'windows_fake_fs', 'fake', 'file']
  },
  [TOKENS_TYPE.WEB_IMAGE]: {
    label: 'Web image',
    description: 'Get an alert when an image you upload to us is viewed.',
    documentationLink:
      'https://docs.canarytokens.org/guide/web-image-token.html',
    icon: `${TOKENS_TYPE.WEB_IMAGE}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish:',
    howItWorksInstructions: [
      'We give you a unique image.',
      'You place it somewhere.',
      'We send you an alert if an attacker view your image.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: ['url', 'img']
  },
  [TOKENS_TYPE.AZURE_ID]: {
    label: 'Azure login certificate',
    description:
      'Get an alert when an attacker uses your Azure Service Principal certificate to login with.',
    documentationLink: '',
    icon: `${TOKENS_TYPE.AZURE_ID}.png`,
    instruction: 'Save this json config file along with the certificate:',
    howItWorksInstructions: [
      'We give you a unique certificate to login.',
      'You place it somewhere.',
      'We send you an alert if an attacker tries to login with your Azure Service Principal.',
    ],
    category: TOKEN_CATEGORY.CLOUD,
    keywords: ['cloud']
  },
  [TOKENS_TYPE.MICROSOFT_EXCEL]: {
    label: 'Microsoft Excel',
    description:
      'Get an alert when an attacker opens your Microsoft Excel document.',
    documentationLink:
      'https://docs.canarytokens.org/guide/ms-excel-token.html',
    icon: `${TOKENS_TYPE.MICROSOFT_EXCEL}.png`,
    instruction: '',
    howItWorksInstructions: [
      'We give you a unique Microsoft Excel document.',
      'You place it somewhere.',
      'We send you an alert if an attacker tries to open the file.',
    ],
    category: TOKEN_CATEGORY.MICROSOFT,
    keywords: ['office']
  },
  [TOKENS_TYPE.MICROSOFT_WORD]: {
    label: 'Microsoft Word',
    description:
      'Get an alert when an attacker opens your Microsoft Word document.',
    documentationLink:
      'https://docs.canarytokens.org/guide/ms-excel-token.html',
    icon: `${TOKENS_TYPE.MICROSOFT_WORD}.png`,
    instruction: '',
    howItWorksInstructions: [
      'We give you a unique Microsoft Word document.',
      'You place it somewhere.',
      'We send you an alert if an attacker tries to open the file.',
    ],
    category: TOKEN_CATEGORY.MICROSOFT,
    keywords: ['office']
  },
  [TOKENS_TYPE.SVN]: {
    label: 'SVN',
    description: 'Get an alert when an attacker checks out an SVN repository.',
    documentationLink: 'https://docs.canarytokens.org/guide/svn-token.html',
    icon: `${TOKENS_TYPE.SVN}.png`,
    instruction: 'Run this SVN command in a dummy repo:',
    howItWorksInstructions: [
      'We give you a unique SVN token.',
      'You place it somewhere.',
      'We send you an alert if an attacker tries checks out an SVN repository.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: []
  },
  [TOKENS_TYPE.UNIQUE_EMAIL]: {
    label: 'Unique email address',
    description:
      'Get an alert when an attacker sends an email to this unique address.',
    documentationLink: '',
    icon: `${TOKENS_TYPE.UNIQUE_EMAIL}.png`,
    instruction: 'Here is a unique email address:',
    howItWorksInstructions: [
      'We give you a unique email address.',
      'You place it somewhere.',
      'We send you an alert if an attacker sends an email to this unique address.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: []
  },
  [TOKENS_TYPE.SQL_SERVER]: {
    label: 'Microsoft SQL Server',
    description:
      'Get an alert when an attacker accesses your MS SQL Server database.',
    documentationLink:
      'https://docs.canarytokens.org/guide/sql-server-token.html',
    icon: `${TOKENS_TYPE.SQL_SERVER}.png`,
    instruction:
      'The next step is to copy the SQL snippet below and run it in your SQL Server database.',
    howItWorksInstructions: [
      'We give you a SQL snippet to run into your database.',
      'You place it somewhere.',
      'We send you an alert if an attacker accesses your MS SQL Server database.',
    ],
    category: TOKEN_CATEGORY.DATABASE,
    keywords: ['db', 'database']
  },
  [TOKENS_TYPE.CUSTOM_EXE]: {
    label: 'Custom EXE / binary',
    description: 'Get an alert when an attacker execute an EXE or DLL file.',
    documentationLink:
      'https://docs.canarytokens.org/guide/custom-exe-token.html',
    icon: `${TOKENS_TYPE.CUSTOM_EXE}.png`,
    instruction: 'Save this file and deploy on Windows machines:',
    howItWorksInstructions: [
      'We give you a tokenized EXE or DLL file.',
      'You place it somewhere.',
      'We send you an alert if an attacker executes an EXE or DLL file.',
    ],
    category: TOKEN_CATEGORY.MICROSOFT,
    keywords: ['windows', 'executable', 'file', 'dll']
  },
  [TOKENS_TYPE.PDF]: {
    label: 'Acrobat Reader PDF',
    description:
      'Get an alert when an attacker opens your PDF document in Acrobat Reader.',
    documentationLink:
      'https://docs.canarytokens.org/guide/adobe-pdf-token.html',
    icon: `${TOKENS_TYPE.PDF}.png`,
    instruction: '',
    howItWorksInstructions: [
      'We give you a PDF document.',
      'You place it somewhere.',
      'We send you an alert if an attacker opens your PDF document in Acrobat Reader.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: ['document']
  },
  [TOKENS_TYPE.WINDOWS_FOLDER]: {
    label: 'Windows Folder',
    description:
      'Get an alert when an attacker browses your Windows Folder in Windows Explorer.',
    documentationLink:
      'https://docs.canarytokens.org/guide/windows-directory-token.html',
    icon: `${TOKENS_TYPE.WINDOWS_FOLDER}.png`,
    instruction: '',
    howItWorksInstructions: [
      'We give you a .ini file.',
      'You place it somewhere inside a folder on a Windows machine.',
      'We send you an alert if an attacker browses your Windows Folder in Windows Explorer.',
    ],
    category: TOKEN_CATEGORY.MICROSOFT,
    keywords: ['ini']
  },
  [TOKENS_TYPE.CLONED_WEBSITE]: {
    label: 'JS cloned website',
    description:
      'Get an alert (using Javascript) when an attacker clones your website.',
    documentationLink:
      'https://docs.canarytokens.org/guide/cloned-web-token.html',
    icon: `${TOKENS_TYPE.CLONED_WEBSITE}.png`,
    instruction: 'Place this Javascript on the page you wish to protect:',
    howItWorksInstructions: [
      'We give you a Javascript snippet.',
      'You place it somewhere in your website.',
      'We send you an alert if an attacker clones your website.',
    ],
    category: TOKEN_CATEGORY.PHISHING,
    keywords: ['javascript', 'web', 'cloned']
  },
  [TOKENS_TYPE.CSS_CLONED_SITE]: {
    label: 'CSS cloned website',
    description:
      'Get an alert (using CSS) when an attacker clones your website.',
    documentationLink:
      'https://docs.canarytokens.org/guide/css-cloned-site-token.html',
    icon: `${TOKENS_TYPE.CSS_CLONED_SITE}.png`,
    instruction:
      'Place this CSS on the page you wish to protect, or import it as custom branding:',
    howItWorksInstructions: [
      'We give you a CSS snippet.',
      'You place it somewhere in your website.',
      'We send you an alert if an attacker clones your website.',
    ],
    category: TOKEN_CATEGORY.PHISHING,
    keywords: ['web', 'cloned']
  },
  [TOKENS_TYPE.KUBECONFIG]: {
    label: 'Kubeconfig',
    description: 'Get an alert when an attacker uses your Kubeconfig.',
    documentationLink:
      'https://docs.canarytokens.org/guide/kubeconfig-token.html',
    icon: `${TOKENS_TYPE.KUBECONFIG}.png`,
    instruction: '',
    howItWorksInstructions: [
      'We give you a YAML file.',
      'You place it somewhere.',
      'We send you an alert if an attacker uses your Kubeconfig.',
    ],
    category: TOKEN_CATEGORY.CLOUD,
    keywords: ['cloud', 'kubernetes']
  },
  [TOKENS_TYPE.WIREGUARD]: {
    label: 'WireGuard VPN',
    description:
      'Get an alert when an attacker uses your WireGuard VPN client config.',
    documentationLink:
      'https://docs.canarytokens.org/guide/wireguard-token.html',
    icon: `${TOKENS_TYPE.WIREGUARD}.png`,
    instruction:
      'Scan this QR Code with the WireGuard app on your phone or copy the config below.',
    howItWorksInstructions: [
      'We give you a “fake” WireGuard VPN endpoint.',
      'You place it somewhere.',
      'We send you an alert if an attacker uses your WireGuard VPN client config.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: []
  },
  [TOKENS_TYPE.AZURE_ENTRA_CONFIG]: {
    label: 'Azure Entra ID login',
    description:
      'Get an alert when an attacker phishes your Azure Entra ID login.',
    documentationLink: '',
    icon: `${TOKENS_TYPE.AZURE_ENTRA_CONFIG}.png`,
    instruction:
      "This token can be deployed automatically or manually. It inserts CSS into your Azure tenant's Entra ID login page to detect when the page has been cloned.",
    howItWorksInstructions: [
      'We give you a CSS snippet.',
      'You place it somewhere into your Azure tenant`s Entra ID login page.',
      'We send you an alert if an attacker phishes your Azure Entra ID login.',
    ],
    category: [
      TOKEN_CATEGORY.PHISHING,
      TOKEN_CATEGORY.CLOUD,
      TOKEN_CATEGORY.MICROSOFT,
    ],
    keywords: ['microsoft', 'css', 'cloned']
  },
  [TOKENS_TYPE.WEBDAV]: {
    label: 'Network Folder',
    description:
      'Get an alert when an attacker browsers a mapped Network Folder (WebDAV).',
    documentationLink:
      'https://docs.canarytokens.org/guide/webdav-token.html',
    icon: `${TOKENS_TYPE.WEBDAV}.png`,
    instruction:
      'Map a drive to the host below, with any username and the password below.',
    howItWorksInstructions: [
      'We give you a WebDAV host and credentials',
      'You map a drive to that network folder.',
      'We send you an alert if an attacker browses that folder.',
    ],
    category: TOKEN_CATEGORY.OTHER,
  },
  [TOKENS_TYPE.IDP_APP]: {
    label: 'SAML IdP App',
    description:
      'Get an alert when an attacker opens a fake app from your Identity Provider dashboard.',
    documentationLink: '',
    icon: `${TOKENS_TYPE.IDP_APP}.png`,
    instruction:
      'Use this login URL and entity ID to create a SAML2 app in your Identity Provider. [sth about suggested name-icon combinations?]',
    howItWorksInstructions: [
      'We give you a “fake” SAML2 app endpoint.',
      'You install it in your Identity Provider as an app.',
      'We send you an alert if an attacker tries to log into that app.',
    ],
    category: TOKEN_CATEGORY.OTHER,
    keywords: []
  },
};
