import{T as m}from"./TokenDisplay-6dzg1Rao.js";import{_ as d}from"./ButtonActivateTokenTips.vue_vue_type_script_setup_true_lang-B_1iEdLk.js";import{d as p,r as i,o as l,a as _,q as o,m as a,N as k}from"./index-J02tC-VD.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-BR9ORpqm.js";import"./BaseCopyButton-BZuw-SDk.js";const w={class:"mt-16 text-sm"},T=p({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(s){const e=s,n=i({hostname:e.tokenData.hostname||"",webdav_fs_type:e.tokenData.webdav_fs_type||"",webdav_password:e.tokenData.webdav_password||"",webdav_server:e.tokenData.webdav_server||""});return(r,t)=>(l(),_(k,null,[o(m,{"token-data":n.value},null,8,["token-data"]),t[1]||(t[1]=a("p",{class:"mt-16 text-sm"}," When the WebDAV folder is browsed, your Canarytoken will be triggered. ",-1)),a("p",w,[o(d,{onHowToUse:t[0]||(t[0]=f=>r.$emit("howToUse"))})])],64))}});export{T as default};
