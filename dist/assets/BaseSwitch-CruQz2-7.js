import{d as c,a as o,c as m,f as a,Q as h,h as g,E as s,b as u,n as l,e as f,a6 as r,a7 as t,a8 as v,y}from"./index-DpRmQAbD.js";const k={class:"relative flex flex-col justify-between"},V=["id","value","checked","aria-checked"],_=["for"],B=c({__name:"BaseSwitch",props:{id:{},label:{},helperMessage:{},hasError:{type:Boolean},errorMessage:{},loading:{type:Boolean},modelValue:{type:Boolean}},emits:["update:modelValue"],setup(M,{emit:n}){const i=n;function d(e){i("update:modelValue",e.target.checked)}return(e,b)=>{const p=v;return o(),m("div",k,[a("input",h(e.$attrs,{id:e.id,type:"checkbox",role:"switch",class:"toggle",value:e.modelValue,checked:e.modelValue,"aria-checked":e.modelValue,onChange:d}),null,16,V),a("label",{for:e.id,class:l(["relative",[{multiline:e.helperMessage||e.errorMessage},{loading:e.loading}]])},[g(s(e.label)+" ",1),e.loading?(o(),u(p,{key:0,class:l(["absolute right-[0.6rem]",[e.helperMessage?"top-[0.7rem]":"top-[0.2rem]"]]),height:"1rem",variant:e.modelValue===!0?"secondary":"primary"},null,8,["class","variant"])):f("",!0)],10,_),a("div",null,[r(a("p",{id:"helper",class:"text-xs leading-4 text-grey-500 pr-[3rem]"},s(e.helperMessage),513),[[t,e.helperMessage]]),r(a("p",{id:"error",class:"text-xs leading-4 text-red"},s(e.errorMessage),513),[[t,e.hasError]])])])}}}),C=y(B,[["__scopeId","data-v-d156e5a5"]]);export{C as _};
