// This map controls which manage-page settings are available in the UI for each
// token type. The backend separately stores whether those settings are currently
// enabled or disabled for an individual token.

// If larger work involves changing token settings or expanding the token capabilities model,
// raise it for broader design discussion on Slack before making those changes.

import { TOKENS_TYPE } from '@/components/constants';

export type TokenManageCapabilitiesType = {
  supportsIPIgnore: boolean;
  supportsBrowserScan: boolean;
  supportsCustomImage: boolean;
};

const COMMON_TOKEN_MANAGE_CAPABILITIES: TokenManageCapabilitiesType = {
  supportsIPIgnore: true,
  supportsBrowserScan: false,
  supportsCustomImage: false,
};

const DISABLED_TOKEN_MANAGE_CAPABILITIES: TokenManageCapabilitiesType = {
  supportsIPIgnore: false,
  supportsBrowserScan: false,
  supportsCustomImage: false,
};

function defineTokenManageCapabilities(
  capabilities: Partial<TokenManageCapabilitiesType> = {},
): TokenManageCapabilitiesType {
  return {
    ...COMMON_TOKEN_MANAGE_CAPABILITIES,
    ...capabilities,
  };
}

const TOKEN_MANAGE_CAPABILITIES: Record<string, TokenManageCapabilitiesType> = {
  [TOKENS_TYPE.WEB_BUG]: defineTokenManageCapabilities({
    supportsBrowserScan: true,
  }),
  [TOKENS_TYPE.DNS]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.LOG4SHELL]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.QRCODE]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.MYSQL]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.WEB_IMAGE]: defineTokenManageCapabilities({
    supportsBrowserScan: true,
    supportsCustomImage: true,
  }),
  [TOKENS_TYPE.AWS_KEYS]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.FAST_REDIRECT]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.SLOW_REDIRECT]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.SENSITIVE_CMD]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.WINDOWS_FAKE_FS]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.AZURE_ID]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.MICROSOFT_EXCEL]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.MICROSOFT_WORD]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.SVN]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.UNIQUE_EMAIL]: defineTokenManageCapabilities({
    supportsIPIgnore: false,
  }),
  [TOKENS_TYPE.SQL_SERVER]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.CUSTOM_EXE]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.PDF]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.WINDOWS_FOLDER]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.CSS_CLONED_SITE]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.CLONED_WEBSITE]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.KUBECONFIG]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.WIREGUARD]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.AZURE_ENTRA_CONFIG]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.PWA]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.CREDIT_CARD_V2]: defineTokenManageCapabilities({
    supportsIPIgnore: false,
  }),
  [TOKENS_TYPE.WEBDAV]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.IDP_APP]: defineTokenManageCapabilities({
    supportsBrowserScan: true,
  }),
  [TOKENS_TYPE.AWS_INFRA]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.CROWDSTRIKE_CC]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.SVG]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.MCP]: defineTokenManageCapabilities(),
  [TOKENS_TYPE.LEGACY]: defineTokenManageCapabilities({
    supportsIPIgnore: false,
  }),
};

export function getTokenManageCapabilities(
  tokenType: string | null,
): TokenManageCapabilitiesType {
  if (!tokenType || !TOKEN_MANAGE_CAPABILITIES[tokenType]) {
    return DISABLED_TOKEN_MANAGE_CAPABILITIES;
  }

  return TOKEN_MANAGE_CAPABILITIES[tokenType];
}
