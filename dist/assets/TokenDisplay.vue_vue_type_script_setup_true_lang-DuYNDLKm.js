import{d as w,r as f,z as $,a as r,c as p,f as t,i,E as _,n as B,b as j,e as y,y as N,I as V,u as h,g as b,h as k,j as T,ae as R,p as z,a8 as O,af as S,$ as U,q as W}from"./index-BWqoNE0f.js";import{_ as P}from"./BaseCopyButton-C4Z7yKz7.js";const H={class:"content-block flex items-center justify-between gap-8 sm:gap-24 py-8 px-[1em] text-grey-500 border border-grey-100 rounded-xl bg-white hover:text-grey-700"},Y={class:"flex items-center"},G={class:"block text-xs font-light text-grey-800 mb-1.5"},J=w({__name:"BaseContentBlock",props:{label:{},text:{},copyContent:{type:Boolean},iconName:{}},setup(u){const d=u,o=f(!1),m=()=>{o.value=!0,setTimeout(()=>{o.value=!1},1750)};return(a,e)=>{const n=$("font-awesome-icon"),c=P;return r(),p("span",H,[t("div",Y,[i(n,{class:"min-w-[32px] text-grey-200 text-lg sm:text-xl mr-[8px]","aria-hidden":"true",icon:a.iconName},null,8,["icon"]),t("div",null,[t("span",G,_(d.label),1),t("span",{class:B(["block text-grey-800 font-medium",{copied:o.value}])},_(d.text),3)])]),a.copyContent?(r(),j(c,{key:0,content:d.text,class:"ring-white ring-4",onClick:e[0]||(e[0]=g=>m())},null,8,["content"])):y("",!0)])}}}),K=N(J,[["__scopeId","data-v-d1a5426b"]]),Q={id:"cc-card",class:"w-[280px] h-[11em] sm:w-[20.5em] sm:h-[13em] relative m-auto text-white"},X={class:"absolute top-[60px] sm:top-[75px] left-[20px] sm:left-[25px] text-base sm:text-lg"},Z={class:"absolute top-[85px] sm:top-[100px] left-[20px] sm:left-[25px] text-base sm:text-lg"},tt={class:"absolute top-[135px] sm:top-[160px] left-[20px] sm:left-[25px] text-base sm:text-lg"},et={class:"absolute top-[135px] sm:top-[160px] left-[135px] sm:left-[165px] text-base sm:text-lg"},ot={class:"grid grid-cols-6 p-16 text-sm grid-flow-row-dense gap-8 mt-24 items-center border border-grey-200 rounded-xl shadow-solid-shadow-grey bg-white"},st=w({__name:"CreditCardToken",props:{tokenData:{}},emits:["close"],setup(u,{emit:d}){const o=u;function m(a){var e;return`${(e=a.match(/(\d{4})/g))==null?void 0:e.join(" ")}`}return(a,e)=>{const n=K;return r(),p(V,null,[t("div",Q,[t("span",X,_(o.tokenData.name_on_card),1),t("span",Z,_(m(o.tokenData.card_number)),1),t("span",tt,_(o.tokenData.expiry_month)+"/"+_(o.tokenData.expiry_year),1),t("span",et,_(o.tokenData.cvv),1)]),t("div",ot,[i(n,{class:"col-span-6 xl:col-span-6",label:"Card Name",text:o.tokenData.name_on_card,"icon-name":"id-card","copy-content":""},null,8,["text"]),i(n,{class:"col-span-6 xl:col-span-6",label:"Card Number",text:m(o.tokenData.card_number),"icon-name":"credit-card","copy-content":""},null,8,["text"]),i(n,{class:"col-span-6 lg:col-span-3",label:"Expires",text:`${o.tokenData.expiry_month}/${o.tokenData.expiry_year}`,"icon-name":"calendar-day","copy-content":""},null,8,["text"]),i(n,{class:"col-span-6 lg:col-span-3",label:"CVV",text:o.tokenData.cvv,"icon-name":"lock","copy-content":""},null,8,["text"])])],64)}}}),nt=N(st,[["__scopeId","data-v-73b12c2d"]]),at={class:"payments-portal-container"},lt={class:"payments-portal flex items-center justify-center p-24 border border-grey-200 rounded-xl shadow-solid-shadow-grey relative"},rt={key:0,class:"flex items-center justify-center w-full gap-4"},it={class:"form flex-col gap-[24px] w-[225px] sm:w-[325px]"},ct={class:"flex-col"},dt={style:{position:"relative"}},mt=["value"],pt={class:"visa credit-card"},ut=["src"],_t={class:"mastercard credit-card"},xt=["src"],ft={class:"canary credit-card"},gt=["src"],vt={class:"flex gap-[24px]"},yt={class:"flex-col form-col w-full"},ht=["value"],bt={class:"flex-col form-col w-full"},kt=["value"],wt={key:0,class:"error"},Ct=["disabled"],Dt={key:1},$t={class:"text-center"},Bt={class:"payment-received"},Tt=w({__name:"TriggerDemo",props:{tokenData:{}},emits:["close"],setup(u,{emit:d}){const o=u,m=d,a=f(0),e=f(!1),n=f(!1),c=["This allows you to test alerting, SIEM integrations, etc. without having to try and visit a shop.","While we are providing you with these tokens, we are not doing so to charge money against them (only criminals should do so). In some jurisdictions, this could be considered attempted fraud, so we'd rather you use this testing system instead."];function g(l,s){return Math.random()*(s-l)+l}function M(l){var s;return`${(s=l.match(/(\d{4})/g))==null?void 0:s.join(" ")}`}function F(){const l=document.createElement("canvas"),s=document.querySelector(".payments-portal");s==null||s.appendChild(l),Object.assign(l.style,{position:"absolute",top:"0",left:"0",width:"100%",height:"100%",pointerEvents:"none"}),Object.assign(l,{with:window.innerWidth,height:window.innerHeight});const C=S.create(l,{resize:!0}),v=25*1e3,D=Date.now()+v;let x=2;const E=S.shapeFromText({text:"💵",scalar:1.5});(function A(){const I=D-Date.now(),L=Math.max(200,500*(I/v));x=Math.max(.8,x-.001),C({particleCount:1,startVelocity:0,ticks:L,origin:{x:Math.random()*5,y:Math.random()*x-.2},shapes:[E],gravity:g(.2,.3),scalar:g(1.5,1.5),drift:g(-.4,.4)}),I>0&&requestAnimationFrame(A)})()}async function q(){n.value=!1;try{e.value=!0,await R(o.tokenData.card_id,o.tokenData.card_number),a.value=1,F()}catch(l){console.log(l),n.value=!0}finally{e.value=!1}}return(l,s)=>{const C=z,v=$("font-awesome-icon"),D=O,x=$("RouterLink");return r(),p(V,null,[i(C,{class:"mb-24 w-fit",variant:"info",messages:c}),t("div",at,[t("div",lt,[t("button",{onClick:s[0]||(s[0]=E=>m("close")),class:"close h-[2rem] w-[2rem] font-semibold text-white rounded-full bg-green hover:bg-green-300 transition duration-100"},[i(v,{icon:"times","aria-hidden":"true",class:B(e.value&&"opacity-30")},null,8,["class"])]),a.value===0?(r(),p("div",rt,[t("div",it,[t("div",ct,[s[1]||(s[1]=t("p",{class:"mb-[28px] p-[16px] mt-[24px] lg:mt-[12px]"}," We'll generate a fake transaction that'll trigger alert notifications for this token. ",-1)),s[2]||(s[2]=t("label",{class:"form-label"},"Card Number",-1)),t("div",dt,[t("input",{disabled:"",value:M(o.tokenData.card_number)},null,8,mt),t("div",pt,[t("img",{src:h(b)("icons/credit-card-token/visa.svg")},null,8,ut)]),t("div",_t,[t("img",{src:h(b)("icons/credit-card-token/mastercard.svg")},null,8,xt)]),t("div",ft,[t("img",{src:h(b)("icons/credit-card-token/canary.svg")},null,8,gt)])])]),t("div",vt,[t("div",yt,[s[3]||(s[3]=t("label",{class:"form-label"},"Expiration date",-1)),t("input",{disabled:"",value:`${o.tokenData.expiry_month}/${o.tokenData.expiry_year}`},null,8,ht)]),t("div",bt,[s[4]||(s[4]=t("label",{class:"form-label"},"Security code",-1)),t("input",{disabled:"",value:o.tokenData.cvv},null,8,kt)])]),n.value?(r(),p("div",wt,"Oops... Something went wrong!")):y("",!0),t("button",{type:"button",onClick:q,class:B({loading:e.value}),disabled:e.value},[e.value?(r(),j(D,{key:0,height:"1.5rem",variant:"secondary",class:"absolute left-0 right-0 ml-auto mr-auto"})):y("",!0),s[5]||(s[5]=t("span",null,"Pay $100.00",-1))],10,Ct)])])):a.value===1?(r(),p("div",Dt,[t("div",$t,[s[8]||(s[8]=t("p",{class:"payment-received-header"},"Payment received!",-1)),t("p",Bt,[s[7]||(s[7]=k("You'll get a notification soon if you ")),i(x,{to:`/history/${o.tokenData.auth}/${o.tokenData.token}`,class:"text-green-600 hover:text-green-500 font-bold"},{default:T(()=>s[6]||(s[6]=[k(" haven't already. ")])),_:1},8,["to"])])])])):y("",!0)])])],64)}}}),jt=N(Tt,[["__scopeId","data-v-c50524fa"]]),Nt={class:"flex flex-col items-center min-h-[448px] justify-center"},Et={key:0},It={class:"flex flex-col lg:flex-row justify-center items-center gap-16"},St=["src"],Ft=w({__name:"TokenDisplay",props:{tokenData:{}},setup(u){const d=u,o=f(!1);async function m(){var e,n;const a={fmt:"credit_card_v2",auth:(e=d.tokenData)==null?void 0:e.auth,token:(n=d.tokenData)==null?void 0:n.token};try{const c=await U(a);window.location.href=c.request.responseURL}catch(c){console.log(c,"File download failed")}finally{console.log("Download ready")}}return(a,e)=>{const n=W;return r(),p("div",Nt,[o.value?(r(),j(jt,{key:1,onClose:e[2]||(e[2]=c=>o.value=!1),"token-data":a.tokenData},null,8,["token-data"])):(r(),p("div",Et,[i(nt,{"token-data":a.tokenData},null,8,["token-data"]),t("div",It,[i(n,{variant:"secondary",class:"mt-24",onClick:e[0]||(e[0]=c=>m())},{default:T(()=>e[3]||(e[3]=[k(" Download Credit Card ")])),_:1}),i(n,{class:"mt-24 relative",onClick:e[1]||(e[1]=c=>o.value=!o.value)},{default:T(()=>[e[4]||(e[4]=t("span",{class:"text-grey-800 absolute top-[-20px] right-[-68px] text-sm font-medium rotate-[30deg]"},"Use me!",-1)),t("img",{class:"absolute top-[-4px] right-[-36px]",src:h(b)("icons/label_arrow_1.svg")},null,8,St),e[5]||(e[5]=k(" Test Credit Card "))]),_:1})])]))])}}});export{Ft as _};
