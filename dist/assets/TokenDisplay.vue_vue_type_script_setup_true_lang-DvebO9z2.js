import{d as l,a as i,c as r,i as d,j as u,h as f,$ as p,q as _}from"./index-Cpz0Q2MG.js";const k={class:"flex justify-center"},w=l({__name:"TokenDisplay",props:{tokenData:{}},setup(s){const t=s;async function c(){var o,e;const a={fmt:"kubeconfig",auth:(o=t.tokenData)==null?void 0:o.auth,token:(e=t.tokenData)==null?void 0:e.token};try{const n=await p(a);window.location.href=n.request.responseURL}catch(n){console.log(n,"File download failed")}finally{console.log("Download ready")}}return(a,o)=>{const e=_;return i(),r("div",k,[d(e,{class:"mt-16",onClick:c},{default:u(()=>o[0]||(o[0]=[f("Download your tokened Kubeconfig file")])),_:1})])}}});export{w as _};
