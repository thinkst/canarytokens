let tokenData = null;

export function setTokenData(data) {
  tokenData = data;
}

export function getTokenData() {
  const data = tokenData;
  tokenData = null; // cleanup
  return data;
}
