import{d as m,r as i,a as p,c as l,i as s,f as t,h as f,I as u,p as _}from"./index-IyCK9Hns.js";import{_ as c}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-nzPJmnEL.js";import{_ as d}from"./ButtonActivateTokenTips.vue_vue_type_script_setup_true_lang-BGeUVxe_.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-CGg9O95H.js";import"./BaseCopyButton-DLt3AYnW.js";const k={class:"mt-16 text-sm"},$=m({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(o){const n=i(o.tokenData.hostname||"");return(a,e)=>{const r=_;return p(),l(u,null,[s(c,{"token-url":n.value},null,8,["token-url"]),t("p",k,[e[1]||(e[1]=f(" Remember, it gets triggered whenever someone performs a DNS lookup of the hostname. ")),s(d,{onHowToUse:e[0]||(e[0]=g=>a.$emit("howToUse"))})]),s(r,{class:"mt-24",variant:"info",message:"The source IP address shown in the alert is the DNS server, not the end user."}),e[2]||(e[2]=t("p",{class:"mt-24 text-sm"},null,-1))],64)}}});export{$ as default};
