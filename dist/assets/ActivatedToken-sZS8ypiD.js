import{_ as m}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-BiWj70e1.js";import{_ as l}from"./ButtonActivateTokenTips.vue_vue_type_script_setup_true_lang-DtrLgual.js";import{d,r as o,a as u,c,i as a,f,h as k,I as _}from"./index-BwEl8Aoe.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-BdHVwrN6.js";import"./BaseCopyButton-ddoXOfOr.js";const y={class:"mt-16 text-sm"},w=d({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(n){const t=n,s=o(t.tokenData.token_url||""),r=o(t.tokenData.entity_id||""),p=o(t.tokenData.app_type||"");return(i,e)=>(u(),c(_,null,[a(m,{"token-url":s.value,"entity-id":r.value,"app-type":p.value},null,8,["token-url","entity-id","app-type"]),f("p",y,[e[1]||(e[1]=k(" When the fake app is opened from your IdP dashboard you receive an alert. ")),a(l,{onHowToUse:e[0]||(e[0]=v=>i.$emit("howToUse"))})])],64))}});export{w as default};
