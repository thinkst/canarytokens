import{_ as n}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-D1SyROYZ.js";import{_ as a}from"./ButtonActivateTokenTips.vue_vue_type_script_setup_true_lang-Do3VSv-3.js";import{d as i,r as m,a as l,c as p,i as t,f as d,h as c,I as k}from"./index-DBVwcgNu.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-CKq4KqUD.js";import"./BaseCopyButton-Dj2XHnLN.js";const f={class:"mt-16 text-sm"},$=i({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(o){const s=m(o.tokenData.token_url);return(r,e)=>(l(),p(k,null,[t(n,{"token-url":s.value},null,8,["token-url"]),d("p",f,[e[1]||(e[1]=c(" The token is similar to the Web token, however, when the link is loaded the view will be immediately redirected to the specified redirect URL. ")),t(a,{onHowToUse:e[0]||(e[0]=_=>r.$emit("howToUse"))})])],64))}});export{$ as default};