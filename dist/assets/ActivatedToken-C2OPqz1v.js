import{_ as r}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-DiwztAi0.js";import{_ as m}from"./ButtonActivateTokenTips.vue_vue_type_script_setup_true_lang-Bj-4uvHy.js";import{d as i,r as p,a as l,c as u,i as o,f as c,h as k,I as f}from"./index-DuGugFKu.js";const d={class:"mt-24 text-sm text-center"},x=i({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(a){const t=a,n=p({token:t.tokenData.token||"",auth:t.tokenData.auth_token||""});return(s,e)=>(l(),u(f,null,[o(r,{"token-data":n.value},null,8,["token-data"]),c("p",d,[e[1]||(e[1]=k(" You'll get an alert when someone tries to use your Kubeconfig. ")),o(m,{onHowToUse:e[0]||(e[0]=_=>s.$emit("howToUse"))})])],64))}});export{x as default};
