import axios from 'axios';

axios.defaults.baseURL = 'http://maxoooo.com/';

export function generateToken(form: any) {
  const url = '/api/generate';
  return axios
    .post(url, form)
    .then((response) => response)
    .catch((error) => error.response);
}
