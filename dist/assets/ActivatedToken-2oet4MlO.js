import{d as r,r as i,o as c,a as p,q as t,m as f,p as _,N as d,B as l}from"./index-J02tC-VD.js";import{_ as u}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-fQG0s7tn.js";import{_ as k}from"./ButtonActivateTokenTips.vue_vue_type_script_setup_true_lang-B_1iEdLk.js";const h={class:"mt-24 text-sm"},$=r({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(a){const o=a,n=i({token:o.tokenData.token||"",auth:o.tokenData.auth_token||""});return(s,e)=>{const m=l;return c(),p(d,null,[t(u,{"token-data":n.value},null,8,["token-data"]),f("p",h,[e[1]||(e[1]=_(" You'll get an alert whenever this document is opened in Microsoft Office, on Windows or macOS. ")),t(k,{onHowToUse:e[0]||(e[0]=w=>s.$emit("howToUse"))})]),t(m,{class:"mt-24",variant:"info",message:"You can rename the document without affecting its operation."})],64)}}});export{$ as default};
