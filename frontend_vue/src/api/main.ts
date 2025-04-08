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

export function generateToken(form: any) {
  const formData = new FormData();
  Object.entries(form).forEach(([key, val]) => {
    val !== null && val !== undefined ? formData.append(key, form[key]) : null;
  });

  const url = '/d3aece8093b71007b5ccfedad91ebb11/generate';
  return axios
    .post(url, formData)
    .then((response) => response);
}

export function manageToken(params: TokenAuthType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/manage';
  return axios
    .get(url, { params })
    .then((response) => response);
}

export function downloadAsset(params: DownloadAssetType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/download';
  return axios
    .get(url, { params })
    .then((response) => response);
}

export function settingsToken(params: SettingsTokenType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/settings';
  return axios
    .post(url, params)
    .then((response) => response);
}

export function historyToken(params: TokenAuthType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/history';
  return axios
    .get(url, { params })
    .then((response) => response);
}

export function deleteToken(params: TokenAuthType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/delete';
  return axios
    .post(url, params)
    .then((response) => response);
}

export function getCreditCardDetails(cf_turnstile_response: string) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/credit_card/quota';
  return axios
    .get(url, { params: { cf_turnstile_response } })
    .then((response) => response);
}

export function triggerDemoCreditCardAlert(card_id: string, card_number: string) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/credit_card/demo/trigger';
  return axios
    .post(url, { card_id, card_number })
    .then((response) => response);
}

export function requestAWSInfraRoleSetupCommands(canarytoken: string, auth_token: string, region: string){
    const url = '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/config-start';
  return axios
    .post(url, { canarytoken, auth_token, region })
    .then((response) => response);
}

export function requestAWSInfraRoleCheck(canarytoken: string, auth_token: string, handle: string | null){
      const url = '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/check-role';
  return axios
    .post(url, { canarytoken, auth_token, handle })
    .then((response) => response);
}

export function requestInventoryCustomerAccount(canarytoken: string, auth_token: string, handle: string | null){
        const url = '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/inventory-customer-account';
  return axios
    .post(url, { canarytoken, auth_token, handle })
    .then((response) => response);
}