import{_ as i}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-CzDPQIEe.js";import{d as v,r as u,a as y,c as B,b as l}from"./index-BwEl8Aoe.js";import"./BaseCopyButton-ddoXOfOr.js";const R={key:0},E=v({__name:"ManageToken",props:{tokenBackendResponse:{}},setup(m){var a,o,c,r,t,_,s,d,p,k;const e=m,n=u({token:((c=(o=(a=e.tokenBackendResponse)==null?void 0:a.canarydrop)==null?void 0:o.canarytoken)==null?void 0:c._value)||"",auth:((r=e.tokenBackendResponse.canarydrop)==null?void 0:r.auth)||"",card_id:((t=e.tokenBackendResponse.canarydrop)==null?void 0:t.cc_v2_card_id)||"",name_on_card:((_=e.tokenBackendResponse.canarydrop)==null?void 0:_.cc_v2_name_on_card)||"",card_number:((s=e.tokenBackendResponse.canarydrop)==null?void 0:s.cc_v2_card_number)||"",expiry_month:((d=e.tokenBackendResponse.canarydrop)==null?void 0:d.cc_v2_expiry_month)||"",expiry_year:((p=e.tokenBackendResponse.canarydrop)==null?void 0:p.cc_v2_expiry_year)||"",cvv:((k=e.tokenBackendResponse)==null?void 0:k.canarydrop.cc_v2_cvv)||""});return(f,h)=>n.value?(y(),l(i,{key:1,"token-data":n.value},null,8,["token-data"])):(y(),B("div",R,"Error loading"))}});export{E as default};
