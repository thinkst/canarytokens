import{_ as s}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-BlwFjYWU.js";import{d as c,r as _,a as p,c as k,b as d}from"./index-DMe_VJ3M.js";import"./pwaIconService-Bk6tPBGx.js";const i={key:0},y=c({__name:"ManageToken",props:{tokenBackendResponse:{}},setup(r){var n,o,t;const e=r,a=_({url:((n=e.tokenBackendResponse.canarydrop)==null?void 0:n.generated_url)||"",pwa_icon:((o=e.tokenBackendResponse.canarydrop)==null?void 0:o.pwa_icon)||"",pwa_app_name:((t=e.tokenBackendResponse.canarydrop)==null?void 0:t.pwa_app_name)||""});return(l,m)=>a.value?(p(),d(s,{key:1,"token-data":a.value},null,8,["token-data"])):(p(),k("div",i,"Error loading"))}});export{y as default};