import{d as g,ad as w,r as s,z as b,a9 as k,a6 as x,a as o,c as u,i as T,j as B,u as d,b as _,a2 as D,e as N,y as V}from"./index-pt1RmN_n.js";const j={key:0,class:"fa-sr-only"},z=g({__name:"BaseCopyButton",props:{content:{default:""}},setup(f){const c=f,{isSupported:m,copy:v,copied:i}=w({content:c.content}),e=s("Copy to clipboard"),t=s(!1),n=s(["hover","focus"]);function a(r){return new Promise(l=>setTimeout(l,r))}async function y(){if(!m||!navigator.clipboard)return e.value="Copy not supported";await a(150),n.value=[],t.value=!0,e.value="Copied!",await a(1500),t.value=!1,n.value=["hover","focus"],await a(150),e.value="Copy to clipboard"}function h(){v(c.content),y()}return(r,l)=>{const p=b("font-awesome-icon"),C=k("tooltip");return x((o(),u("button",{class:"h-[2rem] w-[2rem] font-semibold text-white rounded-full bg-green hover:bg-green-300 transition duration-100","aria-label":"Copy to clipboard",onClick:h},[T(D,{name:"fade",mode:"out-in"},{default:B(()=>[d(i)?(o(),_(p,{key:1,"aria-hidden":"true",icon:"check"})):(o(),_(p,{key:0,"aria-hidden":"true",icon:"copy"}))]),_:1}),d(i)?(o(),u("span",j,"Copied content")):N("",!0)])),[[C,{content:e.value,shown:t.value,triggers:n.value}]])}}}),I=V(z,[["__scopeId","data-v-d331c7c5"]]);export{I as _};