import axios from 'axios';

axios.defaults.baseURL = 'https://maxoooo.com/';

type manageTokenType = {
  auth: string | string[];
  token: string | string[];
};

export function generateToken(form: any) {
  const url = '/api/generate';
  return axios
    .post(url, form)
    .then((response) => response)
    .catch((error) => error.response);
}

export function manageToken(params: manageTokenType) {
  const url = '/api/manage';
  return axios
    .get(url, { params })
    .then((response) => response)
    .catch((error) => error.response);
}

export function downloadToken(params: manageTokenType) {
  const url = '/api/download';
  console.log(params);
  return axios
    .get(url, { params })
    .then((response) => response)
    .catch((error) => error.response);
}
