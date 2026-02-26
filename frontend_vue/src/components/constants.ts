/*
TOKENS_TYPE defines a set of token types that are used in various parts of the application.
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
  WINDOWS_FAKE_FS: 'windows_fake_fs',
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
  PWA: 'pwa',
  CREDIT_CARD_V2: 'credit_card_v2',
  WEBDAV: 'webdav',
  IDP_APP: 'idp_app',
  AWS_INFRA: 'aws_infra',
  CROWDSTRIKE_CC: 'crowdstrike_cc',
};

// unique keys to use in the frontend
export const SETTINGS_TYPE = {
  EMAIL: 'EMAIL',
  WEB_HOOK: 'WEB_HOOK',
  BROWSER_SCANNER: 'BROWSER_SCANNER',
  WEB_IMAGE: 'WEB_IMAGE',
  IP_IGNORE: 'IP_IGNORE',
};

// values used in the backend to identify enable settings
// on updadting
export const UPDATE_SETTINGS_BACKEND_TYPE = {
  EMAIL: 'email_enable',
  WEB_HOOK: 'webhook_enable',
  BROWSER_SCANNER: 'browser_scanner_enable',
  WEB_IMAGE: 'web_image_enable',
  IP_IGNORE: 'ip_ignore_enable',
};

// values used in the backend to identify enable settings
// on getting current state
export const GET_SETTINGS_BACKEND_TYPE = {
  EMAIL: 'alert_email_enabled',
  WEB_HOOK: 'alert_webhook_enabled',
  BROWSER_SCANNER: 'browser_scanner_enabled',
  WEB_IMAGE: 'web_image_enabled',
  IP_IGNORE: 'alert_ip_ignore_enabled',
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
  src_ip: 'Source IP',
  loc: 'Location',
  eventName: 'Event Name',
  file_path: 'File Path Accessed',
};

export const TOKEN_CATEGORY = {
  MICROSOFT: 'microsoft',
  PHISHING: 'phishing',
  CLOUD: 'cloud',
  DATABASE: 'database',
  OTHER: 'other',
};

export const ENTRA_ID_FEEDBACK_TYPES = {
  ENTRA_STATUS_HAS_CUSTOM_CSS_ALREADY: 'has_custom_css_already',
  ENTRA_STATUS_ERROR: 'error',
  ENTRA_STATUS_SUCCESS: 'success',
  ENTRA_STATUS_NO_ADMIN_CONSENT: 'no_admin_consent',
};

export const ENTRA_ID_FEEDBACK_MESSAGES = {
  ENTRA_STATUS_HAS_CUSTOM_CSS_ALREADY:
    'Installation failed: your tenant already has a conflicting custom CSS, please manually add the CSS to your portal branding. We have uninstalled our application from your tenant, revoking all of our permissions.',
  ENTRA_STATUS_ERROR:
    'Installation failed: Unable to automatically install the CSS, please manually add the CSS to your portal branding. We have uninstalled our application from you tenant, revoking all of our permissions.',
  ENTRA_STATUS_SUCCESS:
    'Successfully installed the CSS into your Azure tenant. Please wait for a few minutes for the changes to propagate; no further action is needed. We have uninstalled our application from your tenant, revoking all of our permissions.',
  ENTRA_STATUS_NO_ADMIN_CONSENT:
    'Installation failed due to lack of sufficient granted permissions. We have uninstalled our application from your tenant, revoking all of our permissions.',
};

export const TOKEN_HIT_STATUS = {
  ALERTABLE: 'alertable',
  IGNORED_IP: 'ignored_ip',
}

export const ALERT_FILTER_OPTIONS = {
  ALL: 'all',
  NOTIFIED: 'notified',
  IGNORED: 'ignored',
};

export const MAX_UPLOAD_SIZE = 1024 * 1024 * 1;
export const MAX_APP_NAME_LENGTH = 30;

export const TOKEN_COLOR_PALETTES: { [key: string]: Array<string> } = {
  web: ['#424242', '#3B3B3B', '#41D780', '#71E487'],
  dns: ['#38D47F', '#37877E', '#7FF0C2', '#43D88A', '#38907F'],
  log4shell: ['#F2F2F2', '#E84F40', '#F36A5C', '#FDBCB0'],
  qr_code: ['#B4B4B4', '#E2E3E3', '#A0A0A0', '#737373'],
  my_sql: ['#C2E7EF', '#AEDAE6', '#126E93'],
  web_image: ['#888CD8', '#4554AE', '#35AAE9', '#0E3B76', '#11559D'],
  aws_keys: ['#FEBD4C', '#A66E06', '#5E6570', '#FFC977', '#9299A4'],
  fast_redirect: [
    '#FCA00D',
    '#A26F24',
    '#424242',
    '#FE9203',
    '#BB9A38',
    '#5C5C5C',
  ],
  slow_redirect: ['#FCA40F', '#424242', '#F9B219', '#E98906', '#565656'],
  cmd: ['#1AABEE', '#026696', '#9CE5FD'],
  azure_id: ['#38C0F0', '#0070C6', '#31AFE9', '#0B5BA5'],
  ms_excel: ['#33c481', '#45946a', '#108d44', '#185c37', '#107c41'],
  ms_word: ['#2B7CD3', '#1553BA', '#41A5EE', '#185ABD', '#2B6ECC'],
  svn: ['#829ECB', '#89A5D1', '#E0E9F5'],
  smtp: ['#E6E7E8', '#535B67', '#9FF18D', '#4EDA82', '#85EA89'],
  sql_server: ['#BBC1C8', '#FF0000', '#CFD6DD', '#C22625'],
  signed_exe: ['#434850', '#8BEEAB', '#3CD57F', '#69E285'],
  adobe_pdf: ['#BBC1C8', '#FF0000', '#CFD6DD', '#C22625'],
  windows_dir: ['#D2961B', '#FDDD81', '#E5AA2E', '#7A5C09'],
  cssclonedsite: ['#FEFEFE', '#C5C5C5', '#DD3128', '#EE5E4F'],
  clonedsite: ['#42C348', '#4D4D4D', '#67E185', '#D2D2D2'],
  kubeconfig: ['#0055AA', '#4A96E9', '#3190E5', '#327EE5'],
  wireguard: ['#DF8F93', '#AA3F44', '#B95156', '#8E1E21'],
  azure_id_config: ['#09275C', '#89E3FD', '#547EA7', '#275FA1', '#E2FBFE'],
  cc: ['#C6C7C7', '#E3E5E7', '#38897F', '#38D47F', '#414241'],
  pwa: ['#1AABEE', '#026696', '#9CE5FD'],
  credit_card_v2: ['#C6C7C7', '#E3E5E7', '#38897F', '#38D47F', '#414241'],
  windows_fake_fs: ['#2DCA6E', '#93EE7C', '#A2EAC1', '#D2FAC4', '#43CC5F'],
  idp_app: ['#1AABEE', '#026696', '#9CE5FD'],
  aws_infra: ['#FA6A22', '#233243', '#FC9824'],
};

export const IDP_OPTIONS: { value: string; label: string }[] = [
  {
    value: 'gmail',
    label: 'Gmail',
  },
  {
    value: 'outlook',
    label: 'Outlook',
  },
  {
    value: 'gdrive',
    label: 'Google Drive',
  },
  {
    value: 'onedrive',
    label: 'OneDrive',
  },
  {
    value: 'aws',
    label: 'AWS',
  },
  {
    value: 'azure',
    label: 'Azure',
  },
  {
    value: 'gcloud',
    label: 'Google Cloud',
  },
  {
    value: 'zoho',
    label: 'Zoho',
  },
  {
    value: 'salesforce',
    label: 'Salesforce',
  },
  {
    value: 'zendesk',
    label: 'Zendesk',
  },
  {
    value: 'freshbooks',
    label: 'Freshbooks',
  },
  {
    value: 'elasticsearch',
    label: 'Elasticsearch',
  },
  {
    value: 'kibana',
    label: 'Kibana',
  },
  {
    value: 'onepassword',
    label: '1Password',
  },
  {
    value: 'lastpass',
    label: 'LastPass',
  },
  {
    value: 'bitwarden',
    label: 'Bitwarden',
  },
  {
    value: 'sap',
    label: 'SAP',
  },
  {
    value: 'jira',
    label: 'Jira',
  },
  {
    value: 'jamf',
    label: 'JAMF',
  },
  {
    value: 'duo',
    label: 'Duo',
  },
  {
    value: 'intune',
    label: 'Intune',
  },
  {
    value: 'zoom',
    label: 'Zoom',
  },
  {
    value: 'dropbox',
    label: 'Dropbox',
  },
  {
    value: 'github',
    label: 'GitHub',
  },
  {
    value: 'slack',
    label: 'Slack',
  },
  {
    value: 'msteams',
    label: 'MS Teams',
  },
  {
    value: 'ms365',
    label: 'Microsoft 365',
  },
  {
    value: 'gitlab',
    label: 'GitLab',
  },
  {
    value: 'pagerduty',
    label: 'PagerDuty',
  },
  {
    value: 'sage',
    label: 'Sage',
  },
  {
    value: 'virtru',
    label: 'Virtru',
  },
];
