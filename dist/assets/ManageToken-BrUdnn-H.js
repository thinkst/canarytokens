import{_}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-B3Mn4Dvo.js";import{d as l,r as m,a as k,c as y,b as u}from"./index-oMzHRwJc.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-DZf5eRC9.js";import"./BaseCopyButton-CHEgU_jO.js";const B={key:0},C=l({__name:"ManageToken",props:{tokenBackendResponse:{}},setup(i){var n,o,t,r,s,c,p,d;const e=i,a=m({token:((t=(o=(n=e.tokenBackendResponse)==null?void 0:n.canarydrop)==null?void 0:o.canarytoken)==null?void 0:t._value)||"",auth:((r=e.tokenBackendResponse.canarydrop)==null?void 0:r.auth)||"",appId:((s=e.tokenBackendResponse.canarydrop)==null?void 0:s.app_id)||"",displayName:((c=e.tokenBackendResponse.canarydrop)==null?void 0:c.cert_name)||"",fileWithCertAndPrivateKey:((p=e.tokenBackendResponse.canarydrop)==null?void 0:p.cert_file_name)||"",tenant:((d=e.tokenBackendResponse.canarydrop)==null?void 0:d.tenant_id)||""});return(f,R)=>a.value?(k(),u(_,{key:1,"token-data":a.value},null,8,["token-data"])):(k(),y("div",B,"Error loading"))}});export{C as default};
