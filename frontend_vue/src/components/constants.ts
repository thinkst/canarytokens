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
  CLONED_WEBSITE: 'clonedsite',
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
};

/*
ENABLE_SETTINGS_TYPE values are coming from the backend
*/

export const ENABLE_SETTINGS_TYPE = {
  EMAIL: 'email_enable',
  WEB_HOOK: 'webhook_enable',
  BROWSER_SCANNER: 'browser_scanner_enable',
  WEB_IMAGE: 'web_image_enable',
};

export const INCIDENT_LIST_EXPORT = {
  JSON: 'incidentlist_json',
  CSV: 'incidentlist_csv',
};
