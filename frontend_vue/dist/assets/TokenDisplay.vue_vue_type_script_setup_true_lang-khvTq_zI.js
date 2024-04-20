import{d as r,a as d,o as p,c as _,p as s,q as m,B as u,F as f,G as k,H as h}from"./index-DPCVanMx.js";import{a as D}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-C6Z1St6I.js";const C=r({__name:"TokenDisplay",props:{tokenData:{}},setup(l){const e=l,c=d(`{
  "appId": "${e.tokenData.appId}",
  "displayName" : "${e.tokenData.displayName}",
  "fileWithCertAndPrivateKey": "${e.tokenData.fileWithCertAndPrivateKey}",
  "password": null,
  "tenant": "${e.tokenData.tenant}"
  }`);async function i(){var o,t;const n={fmt:"azure_id",auth:(o=e.tokenData)==null?void 0:o.auth,token:(t=e.tokenData)==null?void 0:t.token};try{const a=await k(n);window.location.href=a.request.responseURL}catch(a){console.log(a,"File download failed")}finally{console.log("Donwload ready")}}return(n,o)=>{const t=D,a=h;return p(),_(f,null,[s(t,{lang:"json",label:"JSON config",code:c.value,multiline:"","custom-height":"13rem"},null,8,["code"]),s(a,{class:"mt-16",onClick:i},{default:m(()=>[u("Download Azure Certificate")]),_:1})],64)}}});export{C as _};
