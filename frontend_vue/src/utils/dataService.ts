import type { AssetData } from '@/components/tokens/aws_infra/types.ts';

export type TokenDataType = {
  token: string;
  hostname: string;
  token_url: string;
  auth_token: string;
  email: string;
  webhook_url: string;
  url_components: null;
  error: null;
  error_message: null;
  Url: null;
  token_type: string;
  aws_region: string;
  aws_account_number: string;
  tf_module_prefix: string;
  ingesting: boolean;
  proposed_plan: { assets: AssetData[] | null };
  code_snippet_command: string;
  available_ai_names: number;
  is_managing_token: boolean;
};

let tokenData: TokenDataType | null = null;

export function setTokenData(data: TokenDataType) {
  tokenData = data;
}

export function getTokenData() {
  const data = tokenData;
  return data;
}
