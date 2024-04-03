import { TOKENS_TYPE } from '@/components/constants.ts';
import { ref } from 'vue';
import generateManagedToken from '@/components/tokens/my_sql/generateManagedToken';

type TokenOperationType = {
  label: string;
  description: string;
  documentationLink: string;
  icon: string;
  instruction: string;
  getNewTokenData?: (data: any) => void;
  getManageTokenData?: (data: any) => void;
};

type TokenOperationsType = {
  [key: string]: TokenOperationType;
};

export function useTokens() {
  const tokensOperations = ref<TokenOperationsType>({
    [TOKENS_TYPE.WEBBUG]: {
      label: 'Web Bug Token',
      description: 'An alert when a URL is visited',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.WEBBUG}.png`,
      instruction: 'Copy this URL to your clipboard and use as you wish',
      getNewTokenData: (data) => {
        return data.token_url;
      },
      getManageTokenData: (data) => {
        return data.canarydrop.generated_url;
      },
    },
    [TOKENS_TYPE.DNS]: {
      label: 'DNS Token',
      description: 'An alert when a hostname is requested',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.DNS}.png`,
      instruction: 'Copy this URL to your clipboard and use as you wish',
      getNewTokenData: (data) => {
        return data.token_url;
      },
      getManageTokenData: (data) => {
        return data.canarydrop.generated_url;
      },
    },
    [TOKENS_TYPE.QRCODE]: {
      label: 'QR Code Token',
      description: 'Generate a QR code for physical tokens',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.QRCODE}.png`,
      instruction: 'Use this QR Code to token a physical location or object:',
      getNewTokenData: (data) => {
        return data.qrcode_png;
      },
      getManageTokenData: (data) => {
        return data.qr_code;
      },
    },
    [TOKENS_TYPE.MYSQL]: {
      label: 'MySQL token',
      description: 'Get alerted when a MySQL dump is loaded',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.MYSQL}.png`,
      instruction: '',
      getNewTokenData: (data) => {
        return { code: data.usage, token: data.token, auth: data.auth_token };
      },
      getManageTokenData: (data) => {
        const tokenCode = generateManagedToken(data);
        return {
          code: tokenCode,
          token: data.canarydrop.canarytoken._value,
          auth: data.canarydrop.auth,
        };
      },
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
  });

  return { tokensOperations };
}
