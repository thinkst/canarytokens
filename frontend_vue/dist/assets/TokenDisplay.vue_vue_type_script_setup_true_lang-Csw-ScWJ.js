import{a as s}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-C6Z1St6I.js";import{d as c,a as n,o as _,e as r}from"./index-DPCVanMx.js";const m=c({__name:"TokenDisplay",props:{tokenData:{}},setup(a){const e=a,t=n(`[default]
aws_access_key_id = ${e.tokenData.aws_access_key_id}
aws_secret_access_key = ${e.tokenData.aws_secret_access_key}
output = ${e.tokenData.output}
region = ${e.tokenData.region}`);return(p,i)=>{const o=s;return _(),r(o,{lang:"javascript",label:"AWS token",code:t.value,multiline:"","custom-height":"10rem"},null,8,["code"])}}});export{m as _};
