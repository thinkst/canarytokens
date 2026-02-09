export type BaseFormValuesType = {
  email: string;
  memo: string;
  [key: string]: string | number | undefined;
};

export interface QRCodeTokenBackendType extends NewTokenBackendType {
  qrcode_png: string;
}

type CanaryTokenType = {
  _value: string;
};

type CanaryDropType = {
  generate: null;
  canarytoken: CanaryTokenType;
  triggered_details: {
    hits: [];
    token_type: string;
  };
  memo: string;
  created_at: string;
  auth: string;
  type: string;
  user: {
    name: string;
    email: null;
  };
  generated_url: string;
  generated_hostname: string;
  alert_email_enabled: boolean;
  alert_email_recipient: string;
  alert_sms_enabled: boolean;
  alert_sms_recipient: string;
  alert_webhook_enabled: boolean;
  alert_webhook_url: string;
  alert_failure_count: string;
  web_image_enabled: boolean;
  web_image_path: string;
  redirect_url: string;
  clonedsite: string;
  kubeconfig: string;
  sql_server_sql_action: string;
  sql_server_table_name: string;
  sql_server_view_name: string;
  sql_server_function_name: string;
  sql_server_trigger_name: string;
  file_contents: string;
  file_name: string;
  expected_referrer: string;
  aws_access_key_id: string;
  aws_secret_access_key: string;
  aws_account_id: string;
  aws_output: string;
  aws_region: string;
  app_id: string;
  tenant_id: string;
  cert: string;
  cert_name: string;
  cert_file_name: string;
  browser_scanner_enabled: boolean;
  wg_key: string;
  cmd_process: string;
  windows_fake_fs_root: string;
  windows_fake_fs_file_structure: string;
  slack_api_key: string;
  cc_id: string;
  cc_kind: string;
  cc_number: string;
  cc_cvc: string;
  cc_expiration: string;
  cc_name: string;
  cc_billing_zip: string;
  cc_address: string;
  cc_rendered_html: string;
  cc_rendered_csv: string;
  wg_conf: string;
  pwa_icon: string | null;
  pwa_app_name: string | null;
  cc_v2_card_id: string;
  cc_v2_card_number: string;
  cc_v2_cvv: string;
  cc_v2_expiry_month: string;
  cc_v2_expiry_year: string;
  cc_v2_name_on_card: string;
  webdav_fs_type: string;
  webdav_password: string;
  webdav_server: string;
  idp_app_entity_id: string | null;
  idp_app_type: string | null;
  crowdstrike_client_id: string;
  crowdstrike_client_secret: string;
  crowdstrike_base_url: string;
};

type NullablePartial<T> = { [P in keyof T]: T[P] | null };
export type NullableCanaryDropType = {
  auth: string | boolean;
} & NullablePartial<Omit<CanaryDropType, 'auth'>> & {
    canarytoken: CanaryTokenType;
  } & NullablePartial<Omit<CanaryDropType, 'canarytoken'>>;

export type ManageTokenBackendType = {
  canarydrop: NullableCanaryDropType;
  public_ip: string;
  wg_private_key_seed: string;
  wg_private_key_n: string;
  wg_conf: string;
  wg_qr_code: string;
  qr_code: string;
  clonedsite_js: string;
  clonedsite_css: string;
  force_https: boolean;
  client_id: string;
  cc_v2_card_id: string;
  cc_v2_card_number: string;
  cc_v2_cvv: string;
  cc_v2_expiry_month: string;
  cc_v2_expiry_year: string;
  cc_v2_name_on_card: string;
  aws_region: string;
  aws_account_id: string;
};

export type NewTokenBackendType = {
  token?: string;
  hostname?: string;
  token_url: string;
  auth_token?: string;
  email?: string;
  webhook_url?: string;
  url_components: [string[]];
  error: string | null;
  error_message: string | null;
  Url: string | null;
  token_type: string;
  aws_access_key_id: string;
  aws_secret_access_key: string;
  output: string;
  region: string;
  token_usage: string;
  token_with_usage_info: string | null;
  app_id: string | null;
  tenant_id: string | null;
  cert: string | null;
  cert_name: string | null;
  cert_file_name: string | null;
  unique_email: string;
  file_name: string | null;
  file_contents: string | null;
  clonedsite_js: string | null;
  css: string | null;
  qr_code: string | null;
  wg_conf: string | null;
  client_id: string | null;
  sql_server_function_name: string | null;
  sql_server_sql_action: string | null;
  sql_server_table_name: string | null;
  sql_server_trigger_name: string | null;
  sql_server_view_name: string | null;
  pwa_icon: string | null;
  pwa_app_name: string | null;
  card_id: string | null;
  name_on_card: string | null;
  card_number: string | null;
  cvv: string | null;
  expiry_month: string | null;
  expiry_year: string | null;
  webdav_fs_type: string | null;
  webdav_password: string | null;
  webdav_server: string | null;
  entity_id: string | null;
  app_type: string | null;
  client_id: string | null;
  client_secret: string | null;
  base_url: string | null;
};

export type AsnType = {
  route: string;
  type: string;
  asn: string;
  domain: string;
  name: string;
};

export type GeoInfo = {
  loc?: string;
  org?: string;
  city?: string;
  country?: string;
  region?: string;
  hostname?: string;
  ip: string;
  timezone?: string;
  postal?: string;
  asn?: null | AsnType;
  readme?: string;
  bogon?: boolean | null;
};

export type RequestHeaders = Record<string, string>;

export type CoordsType = {
  coords: GeolocationPosition | null;
};

export type AWSLogDataType = {
  last_used: string | null;
  service_used: string;
  eventName?: string[] | null;
};

export type DecoyResourceType = {
  asset_type: string;
  'Asset Name': string;
  'Request Parameters': string;
};

export type EventType = {
  'Event Name': string;
  'Event Time': string;
  'Account & Region': string;
};

export type IdentityType = {
  'User Identity': string;
  UserAgent: string;
};

export type MetadataType = {
  'Event ID'?: string;
  'ReadOnly Event'?: boolean;
  'Event Category'?: string;
  Classification?: string;
};

export type AdditionalInfoType = {
  javascript?: null | string;
  browser?: null | string;
  mysql_client?: null | string;
  r?: null | string;
  l?: null | string;
  aws_key_log_data?: AWSLogDataType | null;
  file_path?: null | string;
  useragent?: null | string;
  merchant?: string;
  merchant_identifier?: string;
  transaction_amount?: string;
  transaction_currency?: string;
  masked_card_number?: string;
  transaction_date?: string;
  transaction_type?: string;
  status?: string;
  event?: EventType;
  decoy_resource?: DecoyResourceType;
  identity?: IdentityType;
  metadata?: MetadataType;
};


export type HitsType = {
  time_of_hit: number;
  src_ip: string | null;
  geo_info: GeoInfo | null;
  is_tor_relay: boolean | null;
  input_channel: string;
  src_data: null | any;
  useragent: string | null;
  token_type: string;
  request_headers?: RequestHeaders;
  request_args?: Record<string, any>;
  additional_info: AdditionalInfoType;
  last4?: string | null;
  amount?: string | null;
  merchant?: string | null;
  merchant_identifier?: string | null;
  mail?: string | null;
  referer?: string | null;
  referrer?: string | null;
  location?: string | GeolocationPosition | CoordsType | null;
};

export type HistoryType = {
  hits: HitsType[];
  token_type: string;
};

export type HistoryTokenBackendType = {
  history: HistoryType;
  canarydrop: CanaryDropType;
  google_api_key: string | null;
};

export type CreditCardDataType = {
  auth: string;
  token: string;
  name_on_card: string;
  card_number: string;
  expiry_month: string;
  expiry_year: string;
  cvv: string;
};
