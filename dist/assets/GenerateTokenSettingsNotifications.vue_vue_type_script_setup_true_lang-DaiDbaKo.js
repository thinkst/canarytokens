import{d as w,C as v,z as $,a as t,c as m,i as h,h as _,E as f,A as T,r as b,b as u,j as y,f as c,Q as V,ah as M,ai as E,D as N,e as g,u as p,F as S,a6 as B,a7 as k,n as q,w as F}from"./index-vhWZ7xyN.js";const H={class:"relative border flex-1 group flex flex-col px-16 sm:px-24 pt-16 pb-24 bg-white rounded-3xl top-[0px] shadow-solid-shadow-grey border-grey-200"},P={key:0,class:"flex flex-row gap-8 mb-16 text-sm font-semibold text-left text-grey-400"},D={key:1,class:"mb-8"},z=w({__name:"BaseGenerateTokenSettings",props:{settingType:{}},setup(n){const r=n,s=v(()=>{switch(r.settingType){case"Canarytoken":return"gear";default:return"gear"}});return(o,l)=>{const a=$("font-awesome-icon");return t(),m("div",H,[o.settingType?(t(),m("h3",P,[h(a,{icon:s.value,class:"pt-4 text-grey-300","aria-hidden":"true"},null,8,["icon"]),_(" "+f(o.settingType)+" Settings ",1)])):(t(),m("span",D)),T(o.$slots,"default")])}}}),G=["for"],W=w({__name:"BaseLabel",props:{id:{}},setup(n){return(r,s)=>(t(),m("label",{for:r.id,class:"mb-4 ml-4 font-semibold"},[T(r.$slots,"default")],8,G))}}),j=["innerHTML"],I=w({__name:"BaseLabelArrow",props:{id:{},label:{},arrowVariant:{},arrowWordPosition:{}},setup(n){const r=n,s=b(r.label),o=b(r.arrowVariant)||"one",l=v(()=>r.arrowWordPosition?s.value.split(" ").map((d,e)=>e+1===r.arrowWordPosition?`<span class="label-arrow label-arrow__${o.value}" alt="arrow">${d}</span>`:d).join(" "):s.value);return(a,i)=>{const d=W;return t(),u(d,V(a.$attrs,{id:a.id,class:"container relative mb-8"}),{default:y(()=>[c("span",{innerHTML:l.value},null,8,j)]),_:1},16,["id"])}}}),R={class:"h-16 pr-8 mt-4 ml-16"},Q=w({__name:"BaseFormTextField",props:{id:{},label:{},multiline:{type:Boolean},helperMessage:{},placeholder:{},required:{type:Boolean},multilineHeight:{},fullWidth:{type:Boolean},disabled:{type:Boolean},value:{},hasArrow:{type:Boolean},arrowVariant:{},arrowWordPosition:{},maxLength:{}},setup(n){const r=n,s=v(()=>r.multiline?"textarea":"input"),o=M(r,"id"),{value:l,errorMessage:a,handleChange:i}=E(o,void 0,{initialValue:r.value});function d(e){a&&a.value&&i(e)}return N(()=>r.value,e=>{i(e)}),(e,x)=>{const A=W,C=I;return t(),m("div",{class:q(["flex flex-col text-grey-800 textfield-wrapper",{"w-full":e.fullWidth}])},[e.hasArrow?g("",!0):(t(),u(A,{key:0,id:o.value},{default:y(()=>[_(f(e.label),1)]),_:1},8,["id"])),e.hasArrow?(t(),u(C,{key:1,id:o.value,label:e.label,"arrow-variant":e.arrowVariant,"arrow-word-position":e.arrowWordPosition},null,8,["id","label","arrow-variant","arrow-word-position"])):g("",!0),(t(),u(S(s.value),V({id:o.value,value:p(l),class:["px-16 py-8 border resize-none shadow-inner-shadow-grey rounded-3xl border-grey-400 focus:ring-green-600 focus-visible:ring-1",[{"border-red shadow-none":p(a)},{"border-grey-200 bg-grey-100 shadow-none text-grey-300":e.disabled},{"hide-scrollbar":e.multiline}]],style:`height: ${e.multilineHeight}`,placeholder:e.placeholder,"aria-invalid":p(a),"aria-describedby":"helper error",required:e.required,disabled:e.disabled},e.$attrs,{onBlur:p(i),onInput:x[0]||(x[0]=L=>d(L))}),null,16,["id","value","class","style","placeholder","aria-invalid","required","disabled","onBlur"])),c("div",R,[B(c("p",{id:"helper",class:"text-xs leading-4"},f(e.helperMessage),513),[[k,e.helperMessage]]),B(c("p",{id:"error",class:"text-xs leading-4 text-red"},f(p(a)),513),[[k,p(a)]])])],2)}}}),J={class:"flex flex-col gap-8 mb-8"},O=w({__name:"GenerateTokenSettingsNotifications",props:{memoHelperExample:{}},setup(n){const r=b(!1);return(s,o)=>{const l=Q,a=$("font-awesome-icon"),i=z;return t(),u(i,null,{default:y(()=>[c("div",J,[h(l,{id:"email",type:"text",required:"",placeholder:"your-email@email.com",label:"Mail me here when the alert fires","full-width":"","has-arrow":!0,"arrow-variant":"one","arrow-word-position":3})]),h(l,{id:"memo",label:"Remind me of this when the alert fires",placeholder:`E.g: ${s.memoHelperExample}`,multiline:"",required:"","full-width":"","has-arrow":!0,"arrow-variant":"two","arrow-word-position":4},null,8,["placeholder"]),c("button",{class:"flex flex-row items-center self-end gap-8 px-8 py-4 mb-8 text-xs border rounded-full w-fit grow-0 text-grey-400 border-grey-200 hover:text-green-500 hover:border-green-500",onClick:o[0]||(o[0]=F(d=>r.value=!r.value,["prevent"]))},[h(a,{icon:r.value?"minus":"plus"},null,8,["icon"]),o[1]||(o[1]=_(" Add Webhook Notification "))]),r.value?(t(),u(l,{key:0,id:"webhook_url",type:"text",placeholder:"http://your-webhook-url.com",label:"Notify me here when the alert fires","full-width":"","has-arrow":!0,"arrow-variant":"one","arrow-word-position":3})):g("",!0)]),_:1})}}});export{O as _,Q as a,z as b,W as c};
