import{d as i,r as l,a as c,c as m,f as a,i as o,I as d,p as u}from"./index-DuGugFKu.js";import{_ as k}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-CRF0MmgI.js";const _=i({__name:"ActivatedToken",props:{tokenData:{}},setup(n){const t=n,s=l({token:t.tokenData.token||"",auth:t.tokenData.auth_token||"",client_id:t.tokenData.client_id||"",css:t.tokenData.css||""});return(p,e)=>{const r=u;return c(),m(d,null,[e[0]||(e[0]=a("h3",{class:"mb-16 text-lg font-semibold leading-10 text-center text-grey-800"}," How do you want to deploy it? ",-1)),o(k,{"token-data":s.value},null,8,["token-data"]),e[1]||(e[1]=a("p",{class:"mt-16 text-sm"}," When someone clones your site, they'll load the token, which will check whether the referrer domain is expected. If not, it fires the token and you get an alert. ",-1)),o(r,{class:"mt-24",variant:"info",message:"Upload it as a custom branding stylesheet for your Azure Entra ID login portal (requires a P1 or P2 subscription)","text-link":"How?",href:"https://learn.microsoft.com/en-us/entra/fundamentals/how-to-customize-branding",target:"_blank"})],64)}}});export{_ as default};
