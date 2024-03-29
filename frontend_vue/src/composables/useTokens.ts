import { TOKENS_TYPE } from '@/components/constants.ts';
import { ref } from 'vue';

export function useTokens() {
  const tokensOperations = ref({
    [TOKENS_TYPE.WEBBUG]: {
      label: 'Web Bug Token',
      description: 'An alert when a URL is visited',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.WEBBUG}.png`,
      generate: () => {},
    },
    [TOKENS_TYPE.DNS]: {
      label: 'DNS Token',
      description: 'An alert when a hostname is requested',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.DNS}.png`,
      generate: () => {},
    },
    [TOKENS_TYPE.LOG4SHELL]: {
      label: 'Log 4 Shell',
      description:
        'Alert when a log4j logline is vulnerable to CVW-2021-44-228',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.LOG4SHELL}.png`,
      generate: () => {},
    },
    [TOKENS_TYPE.CLONEDWEBSITE]: {
      label: 'Cloned Website Token',
      description: 'Trigger an alert when your website is cloned',
      documentationLink: '#',
      icon: `${TOKENS_TYPE.CLONEDWEBSITE}.png`,
      generate: () => {},
    },
  });

  return { tokensOperations };
}
