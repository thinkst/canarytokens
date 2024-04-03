/* 
This module defines a set of token types that are used in various parts of the application.
!! These token types should match the token_type values coming from the Backend

When you add a new token inside @/components/tokens, 
name the new folder as the token_type

TODO: if possible, we might add a eslint rule 
to check if a folder name matches a TOKENS_TYPE type
*/

export const TOKENS_TYPE = {
  WEBBUG: 'web',
  DNS: 'dns',
  LOG4SHELL: 'log4shell',
  CLONEDWEBSITE: 'clonedsite',
  QRCODE: 'qr_code',
  MYSQL: 'my_sql',
};
