import axios from 'axios';

type AWSInfraRequestPayload = {
  canarytoken?: string;
  auth_token?: string;
  handle?: string;
};

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
}: AWSInfraRequestPayload) {
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
}: AWSInfraRequestPayload) {
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

export function generateDataChoice(
  canarytoken: string,
  auth_token: string,
  asset_type: string,
  asset_field: string
) {
  const url =
    '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/generate-data-choices';
  return axios
    .post(url, { canarytoken, auth_token, asset_type, asset_field })
    .then((response) => response);
}

export function requestTerraformSnippet({
  canarytoken,
  auth_token,
  handle,
}: AWSInfraRequestPayload) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/setup-ingestion';
  const params = {
    canarytoken,
    auth_token,
    handle,
  };
  return axios.post(url, { ...params }).then((response) => response);
}

export function deleteToken({
  canarytoken,
  auth_token,
  handle,
}: AWSInfraRequestPayload) {
  const url = '/d3aece8093b71007b5ccfedad91ebb11/awsinfra/teardown';
  const params = {
    canarytoken,
    auth_token,
    handle,
  };
  return axios.post(url, { ...params }).then((response) => response);
}
