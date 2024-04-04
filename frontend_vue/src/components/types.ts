type CanaryDropType = {
  canarytoken: {
    _value: string;
  };
  triggered_details: {
    hits: any[];
    token_type: string;
  };
  memo: string;
  created_at: string;
  auth: string;
  type: string;
  user: {
    name: string;
    email: string | null;
  };
  generated_url: string;
  generated_hostname: string;
  alert_email_enabled: boolean;
  alert_email_recipient: string | null;
  alert_sms_enabled: boolean;
  alert_sms_recipient: string | null;
  alert_webhook_enabled: boolean;
  alert_webhook_url: string;
  alert_failure_count: number | null;
  web_image_enabled: boolean;
  web_image_path: string | null;
  redirect_url: string | null;
  clonedsite: any;
  kubeconfig: any;
  sql_server_sql_action: any;
  sql_server_table_name: any;
  sql_server_view_name: any;
  sql_server_function_name: any;
  sql_server_trigger_name: any;
  file_contents: any;
  file_name: any;
  expected_referrer: any;
  aws_access_key_id: any;
  aws_secret_access_key: any;
  aws_account_id: any;
  aws_output: any;
  aws_region: any;
  app_id: any;
  tenant_id: any;
  cert: any;
  cert_name: any;
  cert_file_name: any;
  browser_scanner_enabled: boolean;
  wg_key: any;
  cmd_process: any;
  slack_api_key: any;
  cc_id: any;
  cc_kind: any;
  cc_number: any;
  cc_cvc: any;
  cc_expiration: any;
  cc_name: any;
  cc_billing_zip: any;
  cc_address: any;
  cc_rendered_html: any;
  cc_rendered_csv: any;
};

export type ManageTokenType = {
  canarydrop: CanaryDropType;
  public_ip: any;
  wg_private_key_seed: any;
  wg_private_key_n: any;
  wg_conf: any;
  wg_qr_code: any;
  qr_code: any;
  force_https: any;
};

export type BaseFormValuesType = {
  email: string;
  memo: string;
};
