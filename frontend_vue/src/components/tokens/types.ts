export type BaseFormValuesType = {
  email: string;
  memo: string;
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
  force_https: boolean;
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
};

type AsnType = {
  route: string;
  type: string;
  asn: string;
  domain: string;
  name: string;
};

type GeoInfo = {
  loc: string;
  org: string;
  city: string;
  country: string;
  region: string;
  hostname: string;
  ip: string;
  timezone: string;
  postal: string;
  asn: null | AsnType;
  readme: string;
  bogon: string | null;
};

type RequestHeaders = Record<string, string>;

type AWSLogDataType = {
  last_used: string | null;
  service_used: string | null;
};

interface AdditionalInfo {
  javascript: null | string;
  browser: null | string;
  mysql_client: null | string;
  r: null | string;
  l: null | string;
  aws_key_log_data: AWSLogDataType;
}

export type HitsType = {
  time_of_hit: number;
  src_ip: string;
  geo_info: GeoInfo;
  is_tor_relay: boolean;
  input_channel: string;
  src_data: null | any;
  useragent: string;
  token_type: string;
  request_headers: RequestHeaders;
  request_args: Record<string, any>;
  additional_info: AdditionalInfo;
  last4: string | null;
  amount: string | null;
  merchant: string | null;
  mail: string | null;
  referer: string | null;
  location: string | null;
};

export type FormattedHitsType = {
  time_of_hit: string;
  src_ip: string;
  geo_info: {
    loc?: string;
    org?: string;
    city?: string;
    country?: string;
    region?: string;
    hostname?: string;
    ip: string;
    timezone?: string;
    postal?: string;
    asn?: {
      route: string;
      type: string;
      asn: string;
      domain: string;
      name: string;
    } | null;
    readme?: string;
    bogon?: boolean | string | null;
  };
  is_tor_relay: boolean | null;
  basic_info: {
    token_type: string;
    input_channel: string;
    src_data: string;
    useragent: string;
    last4: string | null;
    amount: string | null;
    merchant: string | null;
    mail: string | null;
    referer: string | null;
    location: string | null;
  };
  additional_info: {
    [key: string]: any; // For additional_info fields with dynamic keys and values
    aws_key_log_data: {
      last_used: Date | null;
      service_used: string | null;
    } | null;
  };
};

export type HistoryTokenBackendType = {
  hits: HitsType[];
  token_type: string;
};
