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
  const url = '/d3aece8093b71007b5ccfedad91ebb11/generate';
  return axios
    .post(url, form)
    .then((response) => response)
    .catch((error) => error.response);
}

export function manageToken(params: TokenAuthType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/manage';
  return axios
    .get(url, { params })
    .then((response) => response)
    .catch((error) => error.response);
}

export function downloadAsset(params: DownloadAssetType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/download';
  return axios
    .get(url, { params })
    .then((response) => response)
    .catch((error) => error.response);
}

export function settingsToken(params: SettingsTokenType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/settings';
  return axios
    .post(url, params)
    .then((response) => response)
    .catch((error) => error.response);
}

export function historyToken(params: TokenAuthType) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/history';
  return axios
    .get(url, { params })
    .then((response) => response)
    .catch((error) => error.response);
}
