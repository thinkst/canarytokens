import{T as p}from"./TokenDisplay-5Bv6rJdQ.js";import{d as c,r as k,a as t,c as _,b as m}from"./index-tvY-knJ6.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-DD07ZsCL.js";import"./BaseCopyButton-BSot4VMX.js";const l={key:0},b=c({__name:"ManageToken",props:{tokenBackendResponse:{}},setup(d){var o,n,s,r;const e=d,a=k({hostname:(o=e.tokenBackendResponse.canarydrop)==null?void 0:o.generated_hostname,webdav_fs_type:(n=e.tokenBackendResponse.canarydrop)==null?void 0:n.webdav_fs_type,webdav_password:((s=e.tokenBackendResponse.canarydrop)==null?void 0:s.webdav_password)||"",webdav_server:((r=e.tokenBackendResponse.canarydrop)==null?void 0:r.webdav_server)||""});return(v,i)=>a.value?(t(),m(p,{key:1,"token-data":a.value},null,8,["token-data"])):(t(),_("div",l,"Error loading"))}});export{b as default};