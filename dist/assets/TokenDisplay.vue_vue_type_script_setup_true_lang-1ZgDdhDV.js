import{d as i,r as u,z as f,a as d,c as m,f as n,i as l,E as c,n as b,b as k,e as y,y as _,ad as g,I as h,j as C,h as w,$ as v,q as D}from"./index-Ba78S-Tl.js";import{_ as $}from"./BaseCopyButton-w0G9G5-e.js";const B={class:"content-block flex items-center justify-between gap-8 sm:gap-24 py-8 px-[1em] text-grey-500 border border-grey-100 rounded-xl bg-white hover:text-grey-700"},N={class:"flex items-center"},T={class:"block text-xs font-light text-grey-800 mb-1.5"},V=i({__name:"BaseContentBlock",props:{label:{},text:{},copyContent:{type:Boolean},iconName:{}},setup(p){const t=p,a=u(!1),s=()=>{a.value=!0,setTimeout(()=>{a.value=!1},1750)};return(e,o)=>{const r=f("font-awesome-icon"),x=$;return d(),m("span",B,[n("div",N,[l(r,{class:"text-grey-200 mr-8 sm:mr-[.75em] text-lg sm:text-xl","aria-hidden":"true",icon:e.iconName},null,8,["icon"]),n("div",null,[n("span",T,c(t.label),1),n("span",{class:b(["block text-grey-800 font-medium",{copied:a.value}])},c(t.text),3)])]),e.copyContent?(d(),k(x,{key:0,content:t.text,class:"ring-white ring-4",onClick:o[0]||(o[0]=U=>s())},null,8,["content"])):y("",!0)])}}}),j=_(V,[["__scopeId","data-v-47394c61"]]),E={id:"cc-card",class:"w-[280px] h-[11em] sm:w-[20.5em] sm:h-[13em] relative m-auto text-white"},I={class:"absolute top-[60px] sm:top-[75px] left-[20px] sm:left-[25px] text-base sm:text-lg"},q={class:"absolute top-[85px] sm:top-[100px] left-[20px] sm:left-[25px] text-base sm:text-lg"},z={class:"absolute top-[135px] sm:top-[160px] left-[20px] sm:left-[25px] text-base sm:text-lg"},F={class:"absolute top-[135px] sm:top-[160px] left-[135px] sm:left-[165px] text-base sm:text-lg"},A={class:"grid grid-cols-6 p-16 text-sm grid-flow-row-dense gap-8 mt-24 items-center border border-grey-200 rounded-xl shadow-solid-shadow-grey bg-white"},L=i({__name:"CreditCardToken",props:{tokenData:{}},setup(p){const t=p;g({content:t.content});function a(s){var e;return`${(e=s.match(/(\d{4})/g))==null?void 0:e.join(" ")}`}return(s,e)=>{const o=j;return d(),m(h,null,[n("div",E,[n("span",I,c(t.tokenData.name_on_card),1),n("span",q,c(a(t.tokenData.card_number)),1),n("span",z,c(t.tokenData.expiry_month)+"/"+c(t.tokenData.expiry_year),1),n("span",F,c(t.tokenData.cvv),1)]),n("div",A,[l(o,{class:"col-span-6 xl:col-span-4",label:"Card Name",text:t.tokenData.name_on_card,"icon-name":"id-card","copy-content":""},null,8,["text"]),l(o,{class:"col-span-6 xl:col-span-4",label:"Card Number",text:a(t.tokenData.card_number),"icon-name":"credit-card","copy-content":""},null,8,["text"]),l(o,{class:"col-span-3 xl:col-span-2",label:"Expires",text:`${t.tokenData.expiry_month}/${t.tokenData.expiry_year}`,"icon-name":"calendar-day","copy-content":""},null,8,["text"]),l(o,{class:"col-span-3 xl:col-span-2",label:"CVV",text:t.tokenData.cvv,"icon-name":"lock","copy-content":""},null,8,["text"])])],64)}}}),R=_(L,[["__scopeId","data-v-d71afb6b"]]),S={class:"flex flex-col items-center"},J=i({__name:"TokenDisplay",props:{tokenData:{}},setup(p){const t=p;async function a(){var e,o;const s={fmt:"credit_card_v2",auth:(e=t.tokenData)==null?void 0:e.auth,token:(o=t.tokenData)==null?void 0:o.token};try{const r=await v(s);window.location.href=r.request.responseURL}catch(r){console.log(r,"File download failed")}finally{console.log("Download ready")}}return(s,e)=>{const o=D;return d(),m("div",S,[l(R,{"token-data":s.tokenData},null,8,["token-data"]),l(o,{class:"mt-24",onClick:e[0]||(e[0]=r=>a())},{default:C(()=>e[1]||(e[1]=[w(" Download Credit Card ")])),_:1})])}}});export{J as _};
