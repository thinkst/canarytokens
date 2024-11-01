import{_ as s}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-CSLscZ3n.js";import{d as c,r as n,a as _,b as r}from"./index-BWqoNE0f.js";const u=c({__name:"TokenDisplay",props:{tokenData:{}},setup(a){const e=a,t=n(`[default]
aws_access_key_id = ${e.tokenData.aws_access_key_id}
aws_secret_access_key = ${e.tokenData.aws_secret_access_key}
output = ${e.tokenData.output}
region = ${e.tokenData.region}`);return(p,k)=>{const o=s;return _(),r(o,{lang:"javascript",label:"AWS token",code:t.value},null,8,["code"])}}});export{u as _};
