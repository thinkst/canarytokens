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
    label: 'Web Bug Token',
    description: 'An alert when a URL is visited',
    documentationLink: 'https://docs.canarytokens.org/guide/http-token.html',
    icon: `${TOKENS_TYPE.WEB_BUG}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish',
  },
  [TOKENS_TYPE.DNS]: {
    label: 'DNS Token',
    description: 'An alert when a hostname is requested',
    documentationLink: 'https://docs.canarytokens.org/guide/dns-token.html',
    icon: `${TOKENS_TYPE.DNS}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish',
  },
  [TOKENS_TYPE.QRCODE]: {
    label: 'QR Code Token',
    description: 'Generate a QR code for physical tokens',
    documentationLink: 'https://docs.canarytokens.org/guide/qr-code-token.html',
    icon: `${TOKENS_TYPE.QRCODE}.png`,
    instruction: 'Use this QR Code to token a physical location or object:',
  },
  [TOKENS_TYPE.MYSQL]: {
    label: 'MySQL token',
    description: 'Get alerted when a MySQL dump is loaded',
    documentationLink:
      'https://docs.canarytokens.org/guide/mysql-dump-token.html',
    icon: `${TOKENS_TYPE.MYSQL}.png`,
    instruction: '',
  },
  [TOKENS_TYPE.AWS_KEYS]: {
    label: 'AWS keys token',
    description: 'Alert when AWS key is used',
    documentationLink:
      'https://docs.canarytokens.org/guide/aws-keys-token.html',
    icon: `${TOKENS_TYPE.AWS_KEYS}.png`,
    instruction:
      'Copy this credential pair to your clipboard to use as desired:',
  },
  [TOKENS_TYPE.LOG4SHELL]: {
    label: 'Log 4 Shell',
    description: 'Alert when a log4j logline is vulnerable to CVW-2021-44-228',
    documentationLink: '#',
    icon: `${TOKENS_TYPE.LOG4SHELL}.png`,
    instruction:
      'The next step is to copy the log4j snippet below and test your systems for the log4shell issue.',
  },
  [TOKENS_TYPE.FAST_REDIRECT]: {
    label: 'Fast redirect token',
    description: 'Alert when a URL is visited, User is redirected',
    documentationLink:
      'https://docs.canarytokens.org/guide/fast-redirect-token.html',
    icon: `${TOKENS_TYPE.FAST_REDIRECT}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish:',
  },
  [TOKENS_TYPE.SLOW_REDIRECT]: {
    label: 'Slow redirect token',
    description:
      'Alert when a URL is visited, User is redirected (more info collected)',
    documentationLink:
      'https://docs.canarytokens.org/guide/slow-redirect-token.html',
    icon: `${TOKENS_TYPE.SLOW_REDIRECT}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish:',
  },
  [TOKENS_TYPE.SENSITIVE_CMD]: {
    label: 'Sensitive command',
    description: 'Alert when a suspicious Windows command is run',
    documentationLink:
      'https://docs.canarytokens.org/guide/sensitive-cmd-token.html',
    icon: `${TOKENS_TYPE.SENSITIVE_CMD}.png`,
    instruction: '',
  },
  [TOKENS_TYPE.WEB_IMAGE]: {
    label: 'Web Image token',
    description: 'Alert when an image you uploaded is viewed',
    documentationLink:
      'https://docs.canarytokens.org/guide/web-image-token.html',
    icon: `${TOKENS_TYPE.WEB_IMAGE}.png`,
    instruction: 'Copy this URL to your clipboard and use as you wish:',
  },
  [TOKENS_TYPE.AZURE_ID]: {
    label: 'Azure Login Certificate token',
    description:
      'Azure Service Principal certificate that alerts when used to login with.',
    documentationLink: '#',
    icon: `${TOKENS_TYPE.AZURE_ID}.png`,
    instruction: 'Save this json config file along with the certificate:',
  },
  [TOKENS_TYPE.MICROSOFT_EXCEL]: {
    label: 'Microsoft Excel document',
    description: 'Get alerted when a document is opened in Microsoft Excel',
    documentationLink:
      'https://docs.canarytokens.org/guide/ms-excel-token.html',
    icon: `${TOKENS_TYPE.MICROSOFT_EXCEL}.png`,
    instruction: '',
  },
  [TOKENS_TYPE.MICROSOFT_WORD]: {
    label: 'Microsoft Word document',
    description: 'Get alerted when a document is opened in Microsoft Word',
    documentationLink:
      'https://docs.canarytokens.org/guide/ms-excel-token.html',
    icon: `${TOKENS_TYPE.MICROSOFT_WORD}.png`,
    instruction: '',
  },
  [TOKENS_TYPE.SVN]: {
    label: 'SVN token',
    description: 'Alert when someone checks out an SVN repository',
    documentationLink: 'https://docs.canarytokens.org/guide/svn-token.html',
    icon: `${TOKENS_TYPE.SVN}.png`,
    instruction: 'Run this SVN command in a dummy repo:',
  },
  [TOKENS_TYPE.UNIQUE_EMAIL]: {
    label: 'Unique email address',
    description: 'Alert when an email is sent to a unique address',
    documentationLink: '#',
    icon: `${TOKENS_TYPE.UNIQUE_EMAIL}.png`,
    instruction: 'Here is a unique email address:',
  },
};
