import{d,r as k,a as e,c,b as p,i as m,I as u,p as _}from"./index-C7lINlsG.js";import{_ as f}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-BlWjoqv3.js";const g={key:0},v=d({__name:"ManageToken",props:{tokenBackendResponse:{}},setup(i){var a,s,t,r;const o=i,n=k({token:((t=(s=(a=o.tokenBackendResponse)==null?void 0:a.canarydrop)==null?void 0:s.canarytoken)==null?void 0:t._value)||"",auth:((r=o.tokenBackendResponse.canarydrop)==null?void 0:r.auth)||""});return(h,y)=>{const l=_;return e(),c(u,null,[n.value?(e(),p(f,{key:1,"token-data":n.value},null,8,["token-data"])):(e(),c("div",g,"Error loading")),m(l,{class:"mt-32",variant:"warning",message:`This token only works on Windows 10 systems and lower. It does
      not work on Windows 11 or higher. This is because a recent group policy update to
      some versions of Windows defaults to disabling functionality that this token
      relies on to fire.`},null,8,["message"])],64)}}});export{v as default};