import{d as m,r as l,a as c,c as i,i as o,I as _,f as a,p as k}from"./index-CgoPuGfo.js";import{_ as u}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-C13SL391.js";import"./pwaIconService-B2uWxnkw.js";const d=a("p",{class:"mt-16 text-sm text-center"}," The token gets triggered whenever you open the app. ",-1),h=a("p",{class:"mt-24 text-sm"},null,-1),x=m({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(n){const e=n;console.log(e.tokenData);const s=l({url:e.tokenData.token_url||"",pwa_icon:e.tokenData.pwa_icon||"",pwa_app_name:e.tokenData.pwa_app_name||""});return(p,t)=>{const r=k;return c(),i(_,null,[o(u,{"token-data":s.value},null,8,["token-data"]),d,o(r,{class:"mt-24",variant:"info",message:"When you open the token link on your phone, press 'Share', then 'Add to Home Screen' to install.","text-link":"More tips?",onClick:t[0]||(t[0]=()=>p.$emit("howToUse"))},null,8,["message"]),h],64)}}});export{x as default};