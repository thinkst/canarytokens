import{d as i,r as m,a as p,c as l,i as t,f as s,I as u,p as f}from"./index-DuGugFKu.js";import{_ as g}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-DxnqvPgP.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-DZycWzwM.js";import"./BaseCopyButton-BKh1K0nZ.js";const U=i({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(o){const n=m(o.tokenData.token_url);return(r,e)=>{const a=f;return p(),l(u,null,[t(g,{"token-url":n.value},null,8,["token-url"]),e[1]||(e[1]=s("p",{class:"mt-16 text-sm"}," Remember, it gets triggered whenever someone requests the URL. ",-1)),t(a,{class:"mt-24",variant:"info",message:"If the URL is requested as an image (e.g. <img src=''>) then your custom image is served. If the URL is surfed in a browser then a blank page is served with fingerprinting Javascript.","text-link":"More tips?",onClick:e[0]||(e[0]=()=>r.$emit("howToUse"))}),e[2]||(e[2]=s("p",{class:"mt-24 text-sm"},null,-1))],64)}}});export{U as default};
