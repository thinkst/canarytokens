import{d as r,r as i,a as p,c as m,i as t,f as l,I as c,p as f}from"./index-vhWZ7xyN.js";import{_ as k}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-QkyjYPza.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-BOdA5Z2Q.js";import"./BaseCopyButton-BJHcl3mr.js";const g=r({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(o){const s=i(o.tokenData.css||"");return(n,e)=>{const a=f;return p(),m(c,null,[t(k,{"token-snippet":s.value},null,8,["token-snippet"]),e[1]||(e[1]=l("p",{class:"mt-16 text-sm"}," Use this CSS to detect when someone has cloned a webpage. ",-1)),t(a,{class:"mt-24",variant:"info",message:`When someone clones your site, they'll load the token, which will check
    whether the referrer domain is expected. If not, it fires the token and you
    get an alert.`,"text-link":"More tips?",onClick:e[0]||(e[0]=()=>n.$emit("howToUse"))})],64)}}});export{g as default};
