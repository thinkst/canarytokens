import{d as l,a as r,c as i,i as d,j as p,h as _,$ as u,q as m}from"./index-BWqoNE0f.js";const f={class:"flex justify-center"},w=l({__name:"TokenDisplay",props:{tokenData:{}},setup(s){const n=s;async function c(){var o,e;const a={fmt:"msexcel",auth:(o=n.tokenData)==null?void 0:o.auth,token:(e=n.tokenData)==null?void 0:e.token};try{const t=await u(a);window.location.href=t.request.responseURL}catch(t){console.log(t,"File download failed")}finally{console.log("Download ready")}}return(a,o)=>{const e=m;return r(),i("div",f,[d(e,{class:"mt-16",onClick:c},{default:p(()=>o[0]||(o[0]=[_("Download your MS Excel file")])),_:1})])}}});export{w as _};
