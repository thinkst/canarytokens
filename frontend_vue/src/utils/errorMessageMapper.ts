export function errorMessageMapper(error: string) {
  if (error.includes('FAILURE_CHECK_ROLE')) {
    const match = error.match(/AWS account (\d{12})/);
    const accountNumber = match
      ? `AWS account ${match[1]}`
      : 'your AWS account';
    return `We couldn\'t assume the role Canarytokens-Inventory-ReadOnly-Role in ${accountNumber}. Either the account number is wrong, or the AWS setup steps were not completed on your side. Re-check the AWS account number, and that the role and trust policy are in place.`;
  }
  if (error.includes('Name generation limit reached for canarytoken')) {
    return `${error}. You can continue with manual setup.`;
  }
  return error;
}
