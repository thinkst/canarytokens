import{d as i,r as m,a as c,c as p,i as t,f,h as _,I as d,p as l}from"./index-BzxwE5q7.js";import{_ as u}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-CJpiEgdk.js";import{_ as k}from"./ButtonActivateTokenTips.vue_vue_type_script_setup_true_lang-CzRME-4D.js";const h={class:"mt-24 text-sm"},$=i({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(a){const o=a,n=m({token:o.tokenData.token||"",auth:o.tokenData.auth_token||""});return(s,e)=>{const r=l;return c(),p(d,null,[t(u,{"token-data":n.value},null,8,["token-data"]),f("p",h,[e[1]||(e[1]=_(" You'll get an alert whenever this document is opened in Microsoft Office, on Windows or macOS. ")),t(k,{onHowToUse:e[0]||(e[0]=w=>s.$emit("howToUse"))})]),t(r,{class:"mt-24",variant:"info",message:"You can rename the document without affecting its operation."})],64)}}});export{$ as default};
