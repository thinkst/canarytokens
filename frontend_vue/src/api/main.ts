import axios from 'axios';

type ManageTokenType = {
  auth: string | string[];
  token: string | string[];
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
  const url = '/api/generate';
  return axios
    .post(url, form)
    .then((response) => response)
    .catch((error) => error.response);
}

export function manageToken(params: ManageTokenType) {
  const url = '/api/manage';
  return axios
    .get(url, { params })
    .then((response) => response)
    .catch((error) => error.response);
}

export function downloadToken(params: ManageTokenType) {
  const url = '/api/download';
  console.log(params);
  return axios
    .get(url, { params })
    .then((response) => response)
    .catch((error) => error.response);
}

export function settingsToken(params: SettingsTokenType) {
  const url = '/api/settings';
  return axios
    .post(url, params)
    .then((response) => response)
    .catch((error) => error.response);
}
