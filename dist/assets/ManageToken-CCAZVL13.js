import{_ as n}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-Behi5L9s.js";import{d as t,r as c,a as o,c as r,b as _}from"./index-CJrokphj.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-CS7lgGg_.js";const k={key:0},m=t({__name:"ManageToken",props:{tokenBackendResponse:{}},setup(s){const e=s,a=c({aws_access_key_id:e.tokenBackendResponse.canarydrop.aws_access_key_id||"",aws_secret_access_key:e.tokenBackendResponse.canarydrop.aws_secret_access_key||"",output:e.tokenBackendResponse.canarydrop.aws_output||"",region:e.tokenBackendResponse.canarydrop.aws_region||""});return(p,d)=>a.value?(o(),_(n,{key:1,"token-data":a.value},null,8,["token-data"])):(o(),r("div",k,"Error loading"))}});export{m as default};
