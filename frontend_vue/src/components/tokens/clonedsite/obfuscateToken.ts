import JavascriptObfuscator from 'javascript-obfuscator';
export default function obfuscateToken(jsCode: string) {
  const modifyScriptJs = (scriptJs: any, cb: any) => {
    const scriptWrapperMatch = scriptJs.match(/^\s*<script\b[^>]*>([\s\S]*?)<\/script\s*>\s*$/i);
    const innerJs = scriptWrapperMatch ? scriptWrapperMatch[1] : scriptJs;
    const newInnerJs = cb(innerJs);
    // Break up script tag strings otherwise Vue build breaks
    /* eslint-disable-next-line prefer-template,no-useless-concat */
    return '<scri' + 'pt>' + newInnerJs + '</scri' + 'pt>';
  };

  const obfuscatedToken = modifyScriptJs(jsCode, (scriptJs: any) =>
    JavascriptObfuscator.obfuscate(scriptJs, {
      compact: true,
      simplify: true,
      stringArray: true,
      stringArrayRotate: true,
      stringArrayShuffle: true,
      stringArrayCallsTransform: true,
      stringArrayThreshold: 1,
      stringArrayIndexShift: true,
      stringArrayEncoding: ['base64'],
      splitStrings: true,
      splitStringsChunkLength: 4,
    }).getObfuscatedCode()
  );

  return obfuscatedToken;
}
