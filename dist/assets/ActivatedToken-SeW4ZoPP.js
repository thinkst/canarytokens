import{d as r,r as m,a as i,c as p,i as t,f as l,I as c,p as d}from"./index-IyCK9Hns.js";import{_}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-D-XQ2FWe.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-CGg9O95H.js";import"./BaseCopyButton-DLt3AYnW.js";const x=r({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(s){const a=m(s.tokenData.unique_email||"");return(o,e)=>{const n=d;return i(),p(c,null,[t(_,{"token-data":a.value},null,8,["token-data"]),t(n,{class:"mt-24",variant:"info",message:"Remember, it gets triggered whenever someone sends an email to the address.","text-link":"More tips?",onClick:e[0]||(e[0]=()=>o.$emit("howToUse"))}),e[1]||(e[1]=l("p",{class:"mt-24 text-sm"},null,-1))],64)}}});export{x as default};
