import{_ as p}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-BX-m8qWQ.js";import{d as k,r as m,a as s,c as d,b as _}from"./index-DuGugFKu.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-DZycWzwM.js";import"./BaseCopyButton-BKh1K0nZ.js";const i={key:0},y=k({__name:"ManageToken",props:{tokenBackendResponse:{}},setup(r){var n,o,t;const a=r,e=m({token:(t=(o=(n=a.tokenBackendResponse)==null?void 0:n.canarydrop)==null?void 0:o.canarytoken)==null?void 0:t._value,hostname:a.tokenBackendResponse.canarydrop.generated_hostname||""}),c=`${e.value.token}@${e.value.hostname.split(/\.(.+)/)[1]}`;return(l,u)=>e.value?(s(),_(p,{key:1,"token-data":c})):(s(),d("div",i,"Error loading"))}});export{y as default};