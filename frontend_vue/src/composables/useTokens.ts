import { TOKENS_TYPE } from '@/components/constants.ts';
import { ref } from 'vue';

type TokenOperationType = {
  label: string;
  description: string;
  documentationLink: string;
  icon: string;
  instruction: string;
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
    },
    [TOKENS_TYPE.DNS]: {
      label: 'DNS Token',
      description: 'An alert when a hostname is requested',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.DNS}.png`,
      instruction: 'Copy this URL to your clipboard and use as you wish',
    },
    [TOKENS_TYPE.LOG4SHELL]: {
      label: 'Log 4 Shell',
      description:
        'Alert when a log4j logline is vulnerable to CVW-2021-44-228',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.LOG4SHELL}.png`,
      instruction: 'Copy this URL to your clipboard and use as you wish',
    },
    [TOKENS_TYPE.CLONEDWEBSITE]: {
      label: 'Cloned Website Token',
      description: 'Trigger an alert when your website is cloned',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.CLONEDWEBSITE}.png`,
      instruction: 'Copy this URL to your clipboard and use as you wish',
    },
  });

  return { tokensOperations };
}
