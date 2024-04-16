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
  // [TOKENS_TYPE.LOG4SHELL]: {
  //   label: 'Log 4 Shell',
  //   description:
  //     'Alert when a log4j logline is vulnerable to CVW-2021-44-228',
  //   documentationLink: '#',
  //   icon: `${TOKENS_TYPE.LOG4SHELL}.png`,
  //   instruction: 'Copy this URL to your clipboard and use as you wish',
  // },
  // [TOKENS_TYPE.CLONEDWEBSITE]: {
  //   label: 'Cloned Website Token',
  //   description: 'Trigger an alert when your website is cloned',
  //   documentationLink: '#',
  //   icon: `${TOKENS_TYPE.CLONEDWEBSITE}.png`,
  //   instruction: 'Copy this URL to your clipboard and use as you wish',
  // },
};
