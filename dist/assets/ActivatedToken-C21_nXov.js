import{_ as m}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-DYaNBkGn.js";import{_ as i}from"./ButtonActivateTokenTips.vue_vue_type_script_setup_true_lang-BGeUVxe_.js";import{d as l,r as p,a as d,c,i as s,f as n,h as k,I as u}from"./index-IyCK9Hns.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-CGg9O95H.js";import"./BaseCopyButton-DLt3AYnW.js";const f={class:"mt-16 text-sm"},b=l({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(o){var a;const e=o,r=p({hostname:e.tokenData.hostname||"",sql_table_name:e.tokenData.sql_server_table_name||"",sql_trigger_name:e.tokenData.sql_server_trigger_name||"",sql_function_name:((a=e.tokenData)==null?void 0:a.sql_server_function_name)||"",sql_server_view_name:e.tokenData.sql_server_view_name||"",sql_action:e.tokenData.sql_server_sql_action||""});return(_,t)=>(d(),c(u,null,[s(m,{"token-data":r.value},null,8,["token-data"]),t[2]||(t[2]=n("p",{class:"mt-16 text-sm"}," When the actions are run, your Canarytoken will be triggered. ",-1)),n("p",f,[t[1]||(t[1]=k(" Since DNS is used as the underlying transport, the Source IP will be that of a DNS server, not the database server. ")),s(i,{onHowToUse:t[0]||(t[0]=v=>_.$emit("howToUse"))})])],64))}});export{b as default};
