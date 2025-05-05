import axios from 'axios';

type TokenAuthType = {
  auth: string;
  token: string;
};

type DownloadAssetType = {
  fmt: string;
  auth: string;
  token: string;
  encoded?: boolean;
};

export type EnableSettingsOptionType =
  | 'email_enable'
  | 'web_image_enable'
  | 'webhook_enable'
  | 'browser_scanner_enable';

type ValueSettingsOptionType = 'off' | 'on';

export type SettingsTokenType = {
  value: ValueSettingsOptionType;
  token: string;
  auth: string;
  setting: EnableSettingsOptionType;
};

type AWSInfraRoleCheckType = {
  canarytoken?: string;
  auth_token?: string;
  handle?: string;
};

type AWSInventoryType = {
  canarytoken?: string;
  auth_token?: string;
  handle?: string;
};

export function generateToken(form: any) {
  const formData = new FormData();
  Object.entries(form).forEach(([key, val]) => {
    val !== null && val !== undefined ? formData.append(key, form[key]) : null;
  });

  const url = '/d3aece8093b71007b5ccfedad91ebb11/generate';
  return axios.post(url, formData).then((response) => response);
}

export function manageToken(params: TokenAuthType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/manage';
  return axios.get(url, { params }).then((response) => response);
}

export function downloadAsset(params: DownloadAssetType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/download';
  return axios.get(url, { params }).then((response) => response);
}

export function settingsToken(params: SettingsTokenType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/settings';
  return axios.post(url, params).then((response) => response);
}

export function historyToken(params: TokenAuthType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/history';
  return axios.get(url, { params }).then((response) => response);
}

export function deleteToken(params: TokenAuthType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/delete';
  return axios.post(url, params).then((response) => response);
}

export function getCreditCardDetails(cf_turnstile_response: string) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/credit_card/quota';
  return axios
    .get(url, { params: { cf_turnstile_response } })
    .then((response) => response);
}

export function triggerDemoCreditCardAlert(
  card_id: string,
  card_number: string
) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/credit_card/demo/trigger';
  return axios.post(url, { card_id, card_number }).then((response) => response);
}

export function requestAWSInfraRoleSetupCommands(
  canarytoken: string,
  auth_token: string,
  region: string
) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/config-start';
  return axios
    .post(url, { canarytoken, auth_token, region })
    .then((response) => response);
}

export function requestAWSInfraRoleCheck({
  canarytoken,
  auth_token,
  handle,
}: AWSInfraRoleCheckType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/check-role';
  const params = {
    canarytoken,
    auth_token,
    handle,
  };
  return axios.post(url, { ...params }).then((response) => response);
}

export function requestInventoryCustomerAccount({
  canarytoken,
  auth_token,
  handle,
}: AWSInventoryType) {
  const url =
    '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/inventory-customer-account';
  const params = {
    canarytoken,
    auth_token,
    handle,
  };
  return axios.post(url, { ...params }).then((response) => response);
}

export function savePlan(canarytoken: string, auth_token: string, plan: any) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/save-plan';
  return axios
    .post(url, { canarytoken, auth_token, plan })
    .then((response) => response);
}

// export function generateDataChoice(
//   canarytoken: string,
//   auth_token: string,
//   asset_type: string
// ) {
//   const url =
//     '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/generate-data-choices';
//   return axios
//     .post(url, { canarytoken, auth_token, asset_type })
//     .then((response) => response);
// }

// fake call
export function generateDataChoice(
  canarytoken: string,
  auth_token: string,
  asset_type: string
) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        result: 'true',
        message: '',
        proposed_data: 'Lorem ipsum data',
      });
    }, 200);
  });
}

export function requestTerraformSnippet({
  canarytoken,
  auth_token,
  handle,
}: AWSInventoryType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/setup-ingestion';
  const params = {
    canarytoken,
    auth_token,
    handle,
  };
  return axios.post(url, { ...params }).then((response) => response);
}
