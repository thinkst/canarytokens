import{d as w,ah as C,ai as k,o as z,z as p,a as m,c as u,f as c,E as h,i as v,j as r,ak as F,al as O,A as f,n as L,u as a,ac as N,e as P,I as V}from"./index-BzxwE5q7.js";const $=["for"],j={class:"h-8 mt-4 ml-16"},q={key:0,class:"text-xs text-red leading-[0px]"},I=w({__name:"BaseFormSelect",props:{id:{},label:{},options:{},placeholder:{},searchable:{type:Boolean},height:{}},emits:["selectOption"],setup(_,{emit:g}){const i=_,n=C(i,"id"),b=g,{errorMessage:l,handleChange:y,handleBlur:B}=k(n);z(()=>{const e=document.querySelector(".vs__search");e==null||e.addEventListener("focusin",s),e==null||e.addEventListener("blur",s);function s(){const t=document.querySelector(".vs__dropdown-toggle");t==null||t.classList.toggle("focus-visible")}});function d(e){typeof e=="object"&&(e=e.value),y(e),b("selectOption",e)}return(e,s)=>{const t=p("font-awesome-icon"),S=p("v-select");return m(),u(V,null,[c("label",{for:n.value,class:"mt-8 ml-4 font-semibold"},h(e.label),9,$),v(S,{id:n.value,class:L(["v-select",{invalid:a(l)}]),style:N(`--vs-dropdown-height: ${i.height}`),options:e.options,searchable:e.searchable,placeholder:e.placeholder,onInput:d,onBlur:a(B),"onOption:selected":s[0]||(s[0]=o=>d(o))},{"open-indicator":r(({attributes:o})=>[c("span",F(O(o)),[v(t,{icon:"chevron-up",class:"w-6 h-6 hover:text-grey-400"})],16)]),option:r(o=>[f(e.$slots,"option",{option:o,value:o.value})]),"selected-option":r(o=>[f(e.$slots,"selected-option",{option:o,value:o.value})]),_:3},8,["id","class","style","options","searchable","placeholder","onBlur"]),c("div",j,[a(l)?(m(),u("p",q,h(a(l)),1)):P("",!0)])],64)}}});export{I as _};
