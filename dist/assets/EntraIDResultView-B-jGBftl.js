import{d as A,B as p,k as E,r as d,o as f,a3 as s,C as o,a as N,b as R,j as _,f as a,u as C,g,i as n,h as x,a4 as r,p as U,q as v}from"./index-DpRmQAbD.js";import{A as O}from"./AppLayoutOneColumn-CV0K8Hhf.js";import{B}from"./BannerDeviceCanarytools-CZeaGMlb.js";const D={class:"flex flex-col items-center gap-8 mb-24"},w=["src"],M={class:"flex flex-col justify-center p-16 md:p-32 md:mx-32 rounded-xl bg-grey-50 md:max-w-[50vw] w-full"},V=A({__name:"EntraIDResultView",setup(y){const e=p(),u=E(),l=d("token_icons/azure_id_config.png");f(async()=>{Object.values(s).includes(e.params.result)||u.push({name:"error"})});const i=o(()=>e.params.result===s.ENTRA_STATUS_HAS_CUSTOM_CSS_ALREADY?r.ENTRA_STATUS_HAS_CUSTOM_CSS_ALREADY:e.params.result===s.ENTRA_STATUS_ERROR?r.ENTRA_STATUS_ERROR:e.params.result===s.ENTRA_STATUS_NO_ADMIN_CONSENT?r.ENTRA_STATUS_NO_ADMIN_CONSENT:r.ENTRA_STATUS_SUCCESS),c=o(()=>e.params.result===s.ENTRA_STATUS_ERROR?"danger":e.params.result===s.ENTRA_STATUS_NO_ADMIN_CONSENT?"warning":e.params.result===s.ENTRA_STATUS_SUCCESS?"success":"info"),S=()=>{window.close()};return(I,t)=>{const m=U,T=v;return N(),R(O,null,{default:_(()=>[a("div",D,[a("img",{src:C(g)(l.value),class:"h-[4rem]","aria-hidden":"true",alt:" Azure Entra ID login logo"},null,8,w),t[1]||(t[1]=a("h2",{class:"text-xl text-center text-grey-800"}," Automatic Setup Process Complete ",-1))]),a("div",M,[n(m,{class:"mb-16",message:i.value,variant:c.value},null,8,["message","variant"]),n(T,{class:"m-auto",variant:"secondary",onClick:t[0]||(t[0]=b=>S())},{default:_(()=>t[2]||(t[2]=[x("Close Window")])),_:1}),n(B,{class:"my-8"})])]),_:1})}}});export{V as default};
