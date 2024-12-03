import{d as c,r as d,a as p,c as _,i as s,j as f,h as m,I as u,$ as k,q as D}from"./index-pt1RmN_n.js";import{_ as w}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-CKZZ42r-.js";const h=c({__name:"TokenDisplay",props:{tokenData:{}},setup(l){const e=l,r=d(`{
  "appId": "${e.tokenData.appId}",
  "displayName" : "${e.tokenData.displayName}",
  "fileWithCertAndPrivateKey": "${e.tokenData.fileWithCertAndPrivateKey}",
  "password": null,
  "tenant": "${e.tokenData.tenant}"
  }`);async function i(){var a,o;const n={fmt:"azure_id",auth:(a=e.tokenData)==null?void 0:a.auth,token:(o=e.tokenData)==null?void 0:o.token};try{const t=await k(n);window.location.href=t.request.responseURL}catch(t){console.log(t,"File download failed")}finally{console.log("Download ready")}}return(n,a)=>{const o=w,t=D;return p(),_(u,null,[s(o,{lang:"json",label:"JSON config",code:r.value},null,8,["code"]),s(t,{class:"mt-16",onClick:i},{default:f(()=>a[0]||(a[0]=[m("Download Azure Certificate")])),_:1})],64)}}});export{h as _};
