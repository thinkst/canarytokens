import{d as r,a as c,c as i,i as d,j as p,h as _,$ as u,q as f}from"./index-Df32NadT.js";const m={class:"flex justify-center"},w=r({__name:"TokenDisplay",props:{tokenData:{}},setup(s){const n=s;async function l(){var o,e;const a={fmt:"cmd",auth:(o=n.tokenData)==null?void 0:o.auth,token:(e=n.tokenData)==null?void 0:e.token};try{const t=await u(a);window.location.href=t.request.responseURL}catch(t){console.log(t,"File download failed")}finally{console.log("Download ready")}}return(a,o)=>{const e=f;return c(),i("div",m,[d(e,{class:"mt-16",onClick:l},{default:p(()=>o[0]||(o[0]=[_("Download your MS registry file")])),_:1})])}}});export{w as _};
