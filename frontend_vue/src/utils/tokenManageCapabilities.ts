import { TOKENS_TYPE } from '@/components/constants';

export type TokenManageCapabilitiesType = {
  supportsIPIgnore: boolean;
  supportsBrowserScan: boolean;
  supportsCustomImage: boolean;
};

const DEFAULT_TOKEN_MANAGE_CAPABILITIES: TokenManageCapabilitiesType = {
  supportsIPIgnore: true,
  supportsBrowserScan: false,
  supportsCustomImage: false,
};

const DISABLED_TOKEN_MANAGE_CAPABILITIES: TokenManageCapabilitiesType = {
  supportsIPIgnore: false,
  supportsBrowserScan: false,
  supportsCustomImage: false,
};

const TOKEN_MANAGE_CAPABILITIES: Record<string, Partial<TokenManageCapabilitiesType>> = {
  [TOKENS_TYPE.WEB_BUG]: {
    supportsBrowserScan: true,
  },
  [TOKENS_TYPE.CREDIT_CARD_V2]: {
    supportsIPIgnore: false,
  },
  [TOKENS_TYPE.WEB_IMAGE]: {
    supportsBrowserScan: true,
    supportsCustomImage: true,
  },
  [TOKENS_TYPE.UNIQUE_EMAIL]: {
    supportsIPIgnore: false,
  },
  [TOKENS_TYPE.IDP_APP]: {
    supportsBrowserScan: true,
  },
  [TOKENS_TYPE.LEGACY]: {
    supportsIPIgnore: false,
  },
};

export function getTokenManageCapabilities(
  tokenType: string | null,
): TokenManageCapabilitiesType {
  if (!tokenType) {
    return DISABLED_TOKEN_MANAGE_CAPABILITIES;
  }

  return {
    ...DEFAULT_TOKEN_MANAGE_CAPABILITIES,
    ...TOKEN_MANAGE_CAPABILITIES[tokenType],
  };
}
