import{_ as p}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-C0s7qUpT.js";import{d as c,r as d,C as l,a as _,c as f,i as t,f as s,h as u,I as g,p as k}from"./index-DMe_VJ3M.js";import{g as h,_ as v}from"./generateSVNToken-CL8ggQWk.js";import{_ as w}from"./ButtonActivateTokenTips.vue_vue_type_script_setup_true_lang-BULX0f7V.js";import"./BaseCopyButton-OQtnlUmd.js";const T={class:"mt-24 text-sm"},D=c({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(n){const o=d(n.tokenData.hostname),a=l(()=>o.value?h(o.value):"");return(r,e)=>{const m=k,i=p;return _(),f(g,null,[t(v,{"token-data":a.value},null,8,["token-data"]),e[2]||(e[2]=s("p",{class:"mt-16 text-sm"}," Remember, it gets triggered whenever someone clones the SVN repo. ",-1)),t(m,{class:"mt-24",variant:"warning",message:"Don't forget to run the following command after you've added the token:"}),t(i,{class:"mt-16",lang:"bash",code:"svn commit"}),s("p",T,[e[1]||(e[1]=u(" The source IP address shown in the alert is the DNS server, not the end user. ")),t(w,{onHowToUse:e[0]||(e[0]=$=>r.$emit("howToUse"))})])],64)}}});export{D as default};
