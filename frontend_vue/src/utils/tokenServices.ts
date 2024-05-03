import { TOKENS_TYPE } from '@/components/constants.ts';

type TokenServiceType = {
  label: string;
  description: string;
  documentationLink: string;
  icon: string;
  instruction: string;
};

type TokenServicesType = {
  [key: string]: TokenServiceType;
};

export const tokenServices: TokenServicesType = {
  [TOKENS_TYPE.WEB_BUG]: {
    label: 'Web Bug',
    description: 'Get an alert when an attacker visits a URL.',
    documentationLink: 'https://docs.canarytokens.org/guide/http-token.html',
    icon: `${TOKENS_TYPE.WEB_BUG}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish',
  },
  [TOKENS_TYPE.DNS]: {
    label: 'DNS',
    description: 'Get an alert when an attacker resolves a DNS name.',
    documentationLink: 'https://docs.canarytokens.org/guide/dns-token.html',
    icon: `${TOKENS_TYPE.DNS}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish',
  },
  [TOKENS_TYPE.QRCODE]: {
    label: 'QR Code',
    description: 'Get an alert when an attacker follows your QR Code.',
    documentationLink: 'https://docs.canarytokens.org/guide/qr-code-token.html',
    icon: `${TOKENS_TYPE.QRCODE}.png`,
    instruction: 'Use this QR Code to token a physical location or object:',
  },
  [TOKENS_TYPE.MYSQL]: {
    label: 'MySQL',
    description: 'Get an alert when an attacker loads your MySQL dump.',
    documentationLink:
      'https://docs.canarytokens.org/guide/mysql-dump-token.html',
    icon: `${TOKENS_TYPE.MYSQL}.png`,
    instruction: '',
  },
  [TOKENS_TYPE.AWS_KEYS]: {
    label: 'AWS keys',
    description: 'Get an alert when an attacker uses your AWS API Key.',
    documentationLink:
      'https://docs.canarytokens.org/guide/aws-keys-token.html',
    icon: `${TOKENS_TYPE.AWS_KEYS}.png`,
    instruction:
      'Copy this credential pair to your clipboard to use as desired:',
  },
  [TOKENS_TYPE.LOG4SHELL]: {
    label: 'Log4Shell',
    description:
      'Get an alert when a log4j logline is vulnerable to CVW-2021-44-228.',
    documentationLink: '#',
    icon: `${TOKENS_TYPE.LOG4SHELL}.png`,
    instruction:
      'The next step is to copy the log4j snippet below and test your systems for the log4shell issue.',
  },
  [TOKENS_TYPE.FAST_REDIRECT]: {
    label: 'Fast redirect',
    description:
      'Get an alert when an attacker visits your URL (then rediret them).',
    documentationLink:
      'https://docs.canarytokens.org/guide/fast-redirect-token.html',
    icon: `${TOKENS_TYPE.FAST_REDIRECT}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish:',
  },
  [TOKENS_TYPE.SLOW_REDIRECT]: {
    label: 'Slow redirect',
    description:
      'Get an alert when an attacker visits your URL (then rediret them and collect more info).',
    documentationLink:
      'https://docs.canarytokens.org/guide/slow-redirect-token.html',
    icon: `${TOKENS_TYPE.SLOW_REDIRECT}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish:',
  },
  [TOKENS_TYPE.SENSITIVE_CMD]: {
    label: 'Sensitive command',
    description: 'Get an alert when a suspicious Windows command is run.',
    documentationLink:
      'https://docs.canarytokens.org/guide/sensitive-cmd-token.html',
    icon: `${TOKENS_TYPE.SENSITIVE_CMD}.png`,
    instruction: '',
  },
  [TOKENS_TYPE.WEB_IMAGE]: {
    label: 'Web image',
    description: 'Get an alert when an image you upload to us is viewed.',
    documentationLink:
      'https://docs.canarytokens.org/guide/web-image-token.html',
    icon: `${TOKENS_TYPE.WEB_IMAGE}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish:',
  },
  [TOKENS_TYPE.AZURE_ID]: {
    label: 'Azure login certificate',
    description:
      'Get an alert when an attacker uses your Azure Service Principal certificate to login with.',
    documentationLink: '#',
    icon: `${TOKENS_TYPE.AZURE_ID}.png`,
    instruction: 'Save this json config file along with the certificate:',
  },
  [TOKENS_TYPE.MICROSOFT_EXCEL]: {
    label: 'Microsoft Excel document',
    description:
      'Get an alert when an attacker opens your Microsoft Excel document.',
    documentationLink:
      'https://docs.canarytokens.org/guide/ms-excel-token.html',
    icon: `${TOKENS_TYPE.MICROSOFT_EXCEL}.png`,
    instruction: '',
  },
  [TOKENS_TYPE.MICROSOFT_WORD]: {
    label: 'Microsoft Word document',
    description:
      'Get an alert when an attacker opens your Microsoft Word document.',
    documentationLink:
      'https://docs.canarytokens.org/guide/ms-excel-token.html',
    icon: `${TOKENS_TYPE.MICROSOFT_WORD}.png`,
    instruction: '',
  },
  [TOKENS_TYPE.SVN]: {
    label: 'SVN',
    description: 'Get an alert when an attacker checks out an SVN repository.',
    documentationLink: 'https://docs.canarytokens.org/guide/svn-token.html',
    icon: `${TOKENS_TYPE.SVN}.png`,
    instruction: 'Run this SVN command in a dummy repo:',
  },
  [TOKENS_TYPE.UNIQUE_EMAIL]: {
    label: 'Unique email address',
    description:
      'Get an alert when an attacker send an email to this unique address.',
    documentationLink: '#',
    icon: `${TOKENS_TYPE.UNIQUE_EMAIL}.png`,
    instruction: 'Here is a unique email address:',
  },
  [TOKENS_TYPE.SQL_SERVER]: {
    label: 'Microsoft SQL Server',
    description:
      'Get an alert when an attacker accesses your MS SQL Server database.',
    documentationLink:
      'https://docs.canarytokens.org/guide/sql-server-token.html',
    icon: `${TOKENS_TYPE.SQL_SERVER}.png`,
    instruction:
      'The next step is to copy the SQL snippet below and run in your SQL Server database.',
  },
  [TOKENS_TYPE.CUSTOM_EXE]: {
    label: 'Custom exe / binary',
    description: 'Get an alert when an attacker extecute an EXE or DLL file.',
    documentationLink:
      'https://docs.canarytokens.org/guide/custom-exe-token.html',
    icon: `${TOKENS_TYPE.CUSTOM_EXE}.png`,
    instruction: 'Save this file and deploy on Windows machines:',
  },
  [TOKENS_TYPE.PDF]: {
    label: 'Acrobat Reader PDF document',
    description:
      'Get an alert when an attacker open your PDF document in Acrobat Reader.',
    documentationLink:
      'https://docs.canarytokens.org/guide/adobe-pdf-token.html',
    icon: `${TOKENS_TYPE.PDF}.png`,
    instruction: '',
  },
  [TOKENS_TYPE.WINDOWS_FOLDER]: {
    label: 'Windows Folder',
    description:
      'Get an alert when an attacker browses your Windows Folder in Windows Explorer.',
    documentationLink:
      'https://docs.canarytokens.org/guide/windows-directory-token.html',
    icon: `${TOKENS_TYPE.WINDOWS_FOLDER}.png`,
    instruction: '',
  },
  [TOKENS_TYPE.CLONED_WEBSITE]: {
    label: 'Cloned website',
    description: 'Get an alert when an attacker clones your website.',
    documentationLink:
      'https://docs.canarytokens.org/guide/cloned-web-token.html',
    icon: `${TOKENS_TYPE.CLONED_WEBSITE}.png`,
    instruction: 'Place this Javascript on the page you wish to protect:',
  },
  [TOKENS_TYPE.CSS_CLONED_SITE]: {
    label: 'CSS cloned website',
    description:
      'Get an alert when an attacker clones your website (using CSS).',
    documentationLink:
      'https://docs.canarytokens.org/guide/css-cloned-site-token.html',
    icon: `${TOKENS_TYPE.CSS_CLONED_SITE}.png`,
    instruction:
      'Place this CSS on the page you wish to protect, or import it as custom branding:',
  },
  [TOKENS_TYPE.KUBECONFIG]: {
    label: 'Kubeconfig',
    description: 'Get an alert when an attacker uses your Kubeconfig.',
    documentationLink:
      'https://docs.canarytokens.org/guide/css-cloned-site-token.html',
    icon: `${TOKENS_TYPE.KUBECONFIG}.png`,
    instruction: '',
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
  },
  [TOKENS_TYPE.AZURE_ENTRA_CONFIG]: {
    label: 'Azure Entra config ID',
    description:
      'Get an alert when an attacker phishes your Azure Entra ID login.',
    documentationLink: '',
    icon: `${TOKENS_TYPE.AZURE_ENTRA_CONFIG}.png`,
    instruction:
      "This token can be deployed automatically or manually. It inserts CSS into your Azure tenant's Entra ID login page to detect when the page has been cloned",
  },
};
