// import JavascriptObfuscator from 'javascript-obfuscator';
// export default function obfuscateToken(jsCode: string) {
//   const modifyScriptJs = (scriptJs, cb) => {
//     let innerJs = scriptJs.replace(/^<script>/, '');
//     innerJs = innerJs.replace(/<\/script>$/, '');
//     const newInnerJs = cb(innerJs);
//     // Break up script tag strings otherwise Vue build breaks
//     /* eslint-disable-next-line prefer-template,no-useless-concat */
//     return '<scri' + 'pt>' + newInnerJs + '</scri' + 'pt>';
//   };

//   const obfuscatedToken = modifyScriptJs(jsCode, (scriptJs) =>
//     JavascriptObfuscator.obfuscate(scriptJs, {
//       compact: true,
//       simplify: true,
//       stringArray: true,
//       stringArrayRotate: true,
//       stringArrayShuffle: true,
//       stringArrayCallsTransform: true,
//       stringArrayThreshold: 1,
//       stringArrayIndexShift: true,
//       stringArrayEncoding: ['base64'],
//       splitStrings: true,
//       splitStringsChunkLength: 4,
//     }).getObfuscatedCode()
//   );

//   return obfuscatedToken;
// }
