/* 
This module defines a set of token types that are used in various parts of the application.
!! These token types should match the token_type values coming from the Backend

When you add a new token inside @/components/tokens, 
name the new folder as the token_type

TODO: if possible, we might add a eslint rule 
to check if a folder name matches a TOKENS_TYPE type
*/

export const TOKENS_TYPE = {
  WEB_BUG: 'web',
  DNS: 'dns',
  LOG4SHELL: 'log4shell',
  QRCODE: 'qr_code',
  MYSQL: 'my_sql',
  WEB_IMAGE: 'web_image',
  AWS_KEYS: 'aws_keys',
  FAST_REDIRECT: 'fast_redirect',
  SLOW_REDIRECT: 'slow_redirect',
  SENSITIVE_CMD: 'cmd',
  AZURE_ID: 'azure_id',
  MICROSOFT_EXCEL: 'ms_excel',
  MICROSOFT_WORD: 'ms_word',
  SVN: 'svn',
  UNIQUE_EMAIL: 'smtp',
  SQL_SERVER: 'sql_server',
  CUSTOM_EXE: 'signed_exe',
  PDF: 'adobe_pdf',
  WINDOWS_FOLDER: 'windows_dir',
  CSS_CLONED_SITE: 'cssclonedsite',
  CLONED_WEBSITE: 'clonedsite',
  KUBECONFIG: 'kubeconfig',
  WIREGUARD: 'wireguard',
  AZURE_ENTRA_CONFIG: 'azure_id_config',
  CREDIT_CARD: 'cc',
};

// unique keys to use in the frontend
export const SETTINGS_TYPE = {
  EMAIL: 'EMAIL',
  WEB_HOOK: 'WEB_HOOK',
  BROWSER_SCANNER: 'BROWSER_SCANNER',
  WEB_IMAGE: 'WEB_IMAGE',
};

// values used in the backend to identify enable settings
// on updadting
export const UPDATE_SETTINGS_BACKEND_TYPE = {
  EMAIL: 'email_enable',
  WEB_HOOK: 'webhook_enable',
  BROWSER_SCANNER: 'browser_scanner_enable',
  WEB_IMAGE: 'web_image_enable',
};

// values used in the backend to identify enable settings
// on getting current state
export const GET_SETTINGS_BACKEND_TYPE = {
  EMAIL: 'alert_email_enabled',
  WEB_HOOK: 'alert_webhook_enabled',
  BROWSER_SCANNER: 'browser_scanner_enabled',
  WEB_IMAGE: 'web_image_enabled',
};

export const INCIDENT_LIST_EXPORT = {
  JSON: 'incidentlist_json',
  CSV: 'incidentlist_csv',
};

export const INCIDENT_CHANNEL_TYPE_LABELS = {
  aws_keys: 'AWS API Key Token',
  cc: 'Credit Card Token',
  azure_id: 'Azure Login Certificate Token',
};

export const INCIDENT_DETAIL_CUSTOM_LABELS = {
  org: 'Organisation',
  is_tor_relay: 'Tor Known Exit Node',
  aws_keys: 'AWS Access Key ID',
  useragent: 'User-agent',
  src_port: 'Client Source Port',
  session_index: 'Client Handshake ID',
  cmd_user_name: 'User executing command',
  cmd_computer_name: 'Computer executing command',
  last_used: 'Key Last Used',
};
