import{_ as u}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-CcPyLR-q.js";import{d as f,r as g,a as l,c as i,f as a,i as t,j as _,h as y,e as h,I as w,$ as k,q as b,p as x}from"./index-Cpz0Q2MG.js";const v={class:"flex justify-center"},B={key:0},N=f({__name:"TokenDisplay",props:{tokenData:{},displayInfoBox:{type:Boolean}},setup(m){const r=m;async function c(){var e,n;const s={fmt:"cmd",auth:(e=r.tokenData)==null?void 0:e.auth,token:(n=r.tokenData)==null?void 0:n.token};try{const o=await k(s);window.location.href=o.request.responseURL}catch(o){console.log(o,"File download failed")}finally{console.log("Download ready")}}const d=g(`reg import FILENAME /reg:64  
reg import FILENAME /reg:32`);return(s,e)=>{const n=b,o=x,p=u;return l(),i(w,null,[a("div",v,[t(n,{class:"mt-16",onClick:c},{default:_(()=>e[0]||(e[0]=[y("Download your MS registry file")])),_:1})]),s.displayInfoBox?(l(),i("div",B,[t(o,{class:"mt-24",variant:"info",message:`Once installed (with admin permissions) you'll get an alert whenever someone
    (or someone's code) runs your sensitive process.`}),e[1]||(e[1]=a("p",{class:"mt-24 text-sm"}," It will automatically provide the command used, computer the command ran on, and the user invoking the command. ",-1)),e[2]||(e[2]=a("p",{class:"mt-16 text-sm"},null,-1))])):h("",!0),t(o,{class:"mt-24",variant:"warning",message:`In order to ensure that the token fires for both 32-bit and 64-bit
    executables, we suggest installing by running the following commands:`}),t(p,{class:"mt-16",lang:"bash",code:d.value},null,8,["code"])],64)}}});export{N as _};
