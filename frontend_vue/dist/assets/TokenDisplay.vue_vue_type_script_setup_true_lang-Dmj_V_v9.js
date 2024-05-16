import{a as s}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-CActm1hN.js";import{d as c,a as n,o as _,e as r}from"./index-DuX8kg7V.js";const u=c({__name:"TokenDisplay",props:{tokenData:{}},setup(a){const e=a,o=n(`[default]
aws_access_key_id = ${e.tokenData.aws_access_key_id}
aws_secret_access_key = ${e.tokenData.aws_secret_access_key}
output = ${e.tokenData.output}
region = ${e.tokenData.region}`);return(p,k)=>{const t=s;return _(),r(t,{lang:"javascript",label:"AWS token",code:o.value},null,8,["code"])}}});export{u as _};
