import{_ as C,b as F}from"./GenerateTokenSettingsNotifications.vue_vue_type_script_setup_true_lang-DwL5GacY.js";import{d as b,ag as k,ah as M,o as N,z as f,a as i,c as d,f as h,E as v,u as r,e as O,i as s,j as g,al as T,am as I,I as y}from"./index-pt1RmN_n.js";const L=["for"],P={key:0,class:"text-xs text-red ml-[4px] leading-[0px]"},V=b({__name:"BaseFormSelect",props:{id:{},label:{},options:{},placeholder:{}},emits:["selectOption"],setup(p,{emit:a}){const n=k(p,"id"),l=a,{value:m,errorMessage:u,handleChange:w,handleBlur:B}=M(n);N(()=>{const e=document.querySelector(".vs__search");e==null||e.addEventListener("focusin",o),e==null||e.addEventListener("blur",o);function o(){const t=document.querySelector(".vs__dropdown-toggle");t==null||t.classList.toggle("focus-visible")}});function _(e){typeof e=="object"&&(e=e.value),w(e),l("selectOption",e)}return(e,o)=>{const t=f("font-awesome-icon"),x=f("v-select");return i(),d(y,null,[h("label",{for:n.value,class:"mt-8 ml-4 mb-8 font-semibold leading-3"},v(e.label),9,L),r(u)?(i(),d("p",P,v(r(u)),1)):O("",!0),s(x,{id:n.value,class:"v-select",options:e.options,searchable:!1,placeholder:e.placeholder,onInput:_,onBlur:r(B),"onOption:selected":o[0]||(o[0]=c=>_(c))},{"open-indicator":g(({attributes:c})=>[h("span",T(I(c)),[s(t,{icon:"chevron-up",class:"w-6 h-6 hover:text-grey-400"})],16)]),_:1},8,["id","options","placeholder","onBlur"])],64)}}}),q=b({__name:"GenerateTokenForm",setup(p){const a=[{value:"security",label:"Cyber Security"},{value:"defense",label:"Defense"},{value:"it",label:"IT"},{value:"medical",label:"Medical"},{value:"testing",label:"Test Server"}];return(S,n)=>{const l=V,m=F;return i(),d(y,null,[s(m,{"setting-type":"Canarytoken"},{default:g(()=>[s(l,{id:"webdav_fs_type",label:"Folder Contents",options:a,placeholder:"Select dummy folder content"})]),_:1}),s(C,{"memo-helper-example":"Machine and drive letter on which this Network Folder was mapped."})],64)}}});export{q as default};