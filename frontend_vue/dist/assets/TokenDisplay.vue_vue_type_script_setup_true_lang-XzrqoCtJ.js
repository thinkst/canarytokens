import{d as i,r as d,a as p,c as _,i as s,j as f,h as m,I as u,a1 as k,q as D}from"./index-wLQBcC24.js";import{_ as h}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-iLWCuIzP.js";const C=i({__name:"TokenDisplay",props:{tokenData:{}},setup(l){const e=l,c=d(`{
  "appId": "${e.tokenData.appId}",
  "displayName" : "${e.tokenData.displayName}",
  "fileWithCertAndPrivateKey": "${e.tokenData.fileWithCertAndPrivateKey}",
  "password": null,
  "tenant": "${e.tokenData.tenant}"
  }`);async function r(){var o,t;const n={fmt:"azure_id",auth:(o=e.tokenData)==null?void 0:o.auth,token:(t=e.tokenData)==null?void 0:t.token};try{const a=await k(n);window.location.href=a.request.responseURL}catch(a){console.log(a,"File download failed")}finally{console.log("Download ready")}}return(n,o)=>{const t=h,a=D;return p(),_(u,null,[s(t,{lang:"json",label:"JSON config",code:c.value},null,8,["code"]),s(a,{class:"mt-16",onClick:r},{default:f(()=>[m("Download Azure Certificate")]),_:1})],64)}}});export{C as _};
