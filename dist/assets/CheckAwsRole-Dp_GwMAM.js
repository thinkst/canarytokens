import{d as x,r as i,i as L,ar as m,o as c,a as _,m as h,L as T,q as D,b as v,c as k,w as y,p as C,C as A}from"./index-J02tC-VD.js";import{_ as B}from"./GenerateTokenCustomFlow-BMr4Noz2.js";const N={class:"w-full flex text-center flex-col items-center"},V={class:"infra-token__title-wrapper"},O={key:0},M=x({__name:"CheckAwsRole",props:{stepData:{}},emits:["updateStep","storeCurrentStepData","isSettingError"],setup(S,{emit:E}){const a=E,I=S,r=i(!0),t=i(!1),o=i(!1),s=i(""),{token:d,auth_token:f}=I.stepData;L(async()=>{a("isSettingError",!1),await g()});async function g(){r.value=!0,t.value=!1,o.value=!1;try{const e=await m({canarytoken:d,auth_token:f});e.status!==200&&(r.value=!1,t.value=!0,s.value=e.data.message,a("isSettingError",!0));const u=e.data.handle,p=Date.now(),R=5*60*1e3,l=setInterval(async()=>{try{const n=await m({handle:u});if(n.status!==200){r.value=!1,t.value=!0,s.value=n.data.error,a("isSettingError",!0),clearInterval(l);return}if(n.data.error){r.value=!1,t.value=!0,s.value=n.data.error,a("isSettingError",!0),clearInterval(l);return}if(Date.now()-p>=R){t.value=!0,s.value="The operation took too long. Try again.",a("isSettingError",!0),clearInterval(l);return}if(n.data.session_credentials_retrieved){r.value=!1,o.value=!0,a("storeCurrentStepData",{token:d,auth_token:f}),clearInterval(l);return}}catch(n){t.value=!0,s.value=n.message||"An error occurred while checking the Role. Try again",a("isSettingError",!0),clearInterval(l);return}finally{r.value=!1}},5e3)}catch(e){t.value=!0,s.value=e.message,o.value=!1,a("isSettingError",!0)}}return(w,e)=>{const u=A;return c(),_("section",N,[h("div",V,[h("h2",null,T(r.value||t.value?"Checking Role...":"Role Checked!"),1)]),D(B,{"is-loading":r.value,"is-error":t.value,"loading-message":"We are checking the role, hold on","error-message":s.value,"is-success":o.value,"success-message":"All set!"},null,8,["is-loading","is-error","error-message","is-success"]),o.value?(c(),_("p",O,"On the next step you'll be inventoring your account")):v("",!0),o.value?(c(),k(u,{key:1,class:"mt-40",onClick:e[0]||(e[0]=p=>a("updateStep"))},{default:y(()=>e[1]||(e[1]=[C(" Continue to inventory")])),_:1})):v("",!0),t.value?(c(),k(u,{key:2,class:"mt-40",variant:"secondary",onClick:g},{default:y(()=>e[2]||(e[2]=[C(" Try again ")])),_:1})):v("",!0)])}}});export{M as default};
