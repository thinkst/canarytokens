import{d as c,r as d,o as p,a as _,q as s,w as f,p as m,N as u,a1 as k,C as w}from"./index-J02tC-VD.js";import{_ as D}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-BR9ORpqm.js";const h=c({__name:"TokenDisplay",props:{tokenData:{}},setup(l){const e=l,r=d(`{
  "appId": "${e.tokenData.appId}",
  "displayName" : "${e.tokenData.displayName}",
  "fileWithCertAndPrivateKey": "${e.tokenData.fileWithCertAndPrivateKey}",
  "password": null,
  "tenant": "${e.tokenData.tenant}"
  }`);async function i(){var a,o;const n={fmt:"azure_id",auth:(a=e.tokenData)==null?void 0:a.auth,token:(o=e.tokenData)==null?void 0:o.token};try{const t=await k(n);window.location.href=t.request.responseURL}catch(t){console.log(t,"File download failed")}finally{console.log("Download ready")}}return(n,a)=>{const o=D,t=w;return p(),_(u,null,[s(o,{lang:"json",label:"JSON config",code:r.value},null,8,["code"]),s(t,{class:"mt-16",onClick:i},{default:f(()=>a[0]||(a[0]=[m("Download Azure Certificate")])),_:1})],64)}}});export{h as _};
