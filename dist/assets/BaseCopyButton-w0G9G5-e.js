import{d as w,ad as b,r as s,z as g,a9 as k,a6 as x,a as o,c as u,i as T,j as B,u as d,b as _,a2 as D,e as N,y as V}from"./index-Ba78S-Tl.js";const j={key:0,class:"fa-sr-only"},z=w({__name:"BaseCopyButton",props:{content:{default:""}},setup(f){const i=f,{isSupported:m,copy:v,copied:r}=b({content:i.content}),e=s("Copy to clipboard"),t=s(!1),n=s(["hover","focus"]);function a(c){return new Promise(l=>setTimeout(l,c))}async function y(){if(!m)return e.value="Copy not supported";await a(150),n.value=[],t.value=!0,e.value="Copied!",await a(1500),t.value=!1,n.value=["hover","focus"],await a(150),e.value="Copy to clipboard"}function h(){v(i.content),y()}return(c,l)=>{const p=g("font-awesome-icon"),C=k("tooltip");return x((o(),u("button",{class:"h-[2rem] w-[2rem] font-semibold text-white rounded-full bg-green hover:bg-green-300 transition duration-100","aria-label":"Copy to clipboard",onClick:h},[T(D,{name:"fade",mode:"out-in"},{default:B(()=>[d(r)?(o(),_(p,{key:1,"aria-hidden":"true",icon:"check"})):(o(),_(p,{key:0,"aria-hidden":"true",icon:"copy"}))]),_:1}),d(r)?(o(),u("span",j,"Copied content")):N("",!0)])),[[C,{content:e.value,shown:t.value,triggers:n.value}]])}}}),I=V(z,[["__scopeId","data-v-34b88550"]]);export{I as _};
