import{d as m,r,a as d,c as f,i as c,j as k,h as u,E as D,q as h,f as w,I as v}from"./index-DMe_VJ3M.js";import{_ as x}from"./ButtonActivateTokenTips.vue_vue_type_script_setup_true_lang-BULX0f7V.js";const $={class:"flex justify-center"},T=m({__name:"TokenDisplay",props:{tokenData:{}},setup(a){var s,_;const e=a,n=r(`${(s=e.tokenData)==null?void 0:s.file_name}`),o=r((_=e.tokenData)==null?void 0:_.file_contents);function t(){var i,l;o.value=`${(i=e.tokenData)==null?void 0:i.file_name}`,n.value=(l=e.tokenData)==null?void 0:l.file_contents}return(i,l)=>{const p=h;return d(),f("div",$,[c(p,{class:"mt-16",href:n.value,download:o.value,onClick:t},{default:k(()=>[u("Download "+D(e.tokenData.file_name),1)]),_:1},8,["href","download"])])}}}),g={class:"mt-16 text-sm"},b=m({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(a){const e=a,n=r({file_name:e.tokenData.file_name||"",file_contents:e.tokenData.file_contents||""});return(o,t)=>(d(),f(v,null,[c(T,{"token-data":n.value},null,8,["token-data"]),w("p",g,[t[1]||(t[1]=u(" Remember, this token is triggered whenever the binary file is executed. For EXEs, this means direct execution and for DLLs, it means they were loaded. ")),c(x,{onHowToUse:t[0]||(t[0]=s=>o.$emit("howToUse"))})])],64))}});export{b as default};
