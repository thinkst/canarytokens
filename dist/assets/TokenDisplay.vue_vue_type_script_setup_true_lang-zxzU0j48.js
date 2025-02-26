import{d as x,r as w,C as h,z as y,a as i,c as d,f as t,i as n,w as m,e as C,h as u,j as g,a5 as v,I as b,$ as k,q as D}from"./index-Cpz0Q2MG.js";const U={key:0,class:"flex flex-col gap-16 md:flex-row"},B=["href"],R={key:1,class:"relative text-center"},T={class:"flex flex-col gap-[16px] text-center my-16"},_={class:"py-16 bg-white rounded-lg"},S={class:"py-16 bg-white rounded-lg"},N=x({__name:"TokenDisplay",props:{tokenData:{}},setup(p){const a=p,l=w(!1),f=h(()=>{var o;const r=encodeURIComponent(btoa(`${(o=a.tokenData)==null?void 0:o.css}`)),e=`${window.location.origin}/azure_css_landing`;return`https://login.microsoftonline.com/common/adminconsent?client_id=${a.tokenData.client_id}&state=${r}&redirect_uri=${e}`});function c(){l.value=!l.value}async function A(){var e,o;const r={fmt:"cssclonedsite",auth:(e=a.tokenData)==null?void 0:e.auth,token:(o=a.tokenData)==null?void 0:o.token};try{const s=await k(r);window.location.href=s.request.responseURL}catch(s){console.log(s,"File download failed")}finally{console.log("Download ready")}}return(r,e)=>{const o=y("font-awesome-icon"),s=D;return i(),d(b,null,[l.value?C("",!0):(i(),d("div",U,[t("a",{class:"relative border flex-1 group flex flex-col px-24 py-24 bg-white rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200 items-center duration-100 ease-in-out hover:border-green hover:shadow-solid-shadow-green-500-md hover:top-[-0.2em]",href:f.value,target:"_blank"},[n(o,{icon:"robot","aria-hidden":"true",class:"h-[2rem] text-green-200 mb-[16px]"}),e[0]||(e[0]=t("span",{class:"font-semibold text-grey-500"},"Automatic flow",-1)),e[1]||(e[1]=t("span",{class:"text-sm text-grey-400"},"You give us access to manage your Entra setup",-1))],8,B),t("button",{class:"relative border flex-1 group flex flex-col px-24 py-24 bg-white rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200 items-center duration-100 ease-in-out hover:border-green hover:shadow-solid-shadow-green-500-md hover:top-[-0.2em]",onClick:m(c,["stop"])},[n(o,{icon:"hands","aria-hidden":"true",class:"h-[2rem] text-green-200 mb-[16px]"}),e[2]||(e[2]=t("span",{class:"font-semibold text-grey-500"},"Manual flow",-1)),e[3]||(e[3]=t("span",{class:"text-sm text-grey-400"},"You insert the token manually yourself",-1))])])),l.value?(i(),d("div",R,[t("div",null,[e[10]||(e[10]=t("h3",{class:"font-semibold text-center text-md text-grey-800"}," Manual Flow ",-1)),t("button",{class:"text-sm font-semibold text-center md:absolute text-grey-300 hover:text-green-500 top-4 md:left-[0px]",onClick:m(c,["stop"])},[n(o,{icon:"arrow-left","aria-hidden":"true"}),e[4]||(e[4]=u(" Not sure? Go Back "))]),t("ul",T,[t("li",_,[e[6]||(e[6]=t("p",{class:"mb-8 text-sm"},"Download the necessary CSS:",-1)),n(s,{variant:"secondary",onClick:A},{default:g(()=>e[5]||(e[5]=[u("Download CSS")])),_:1})]),n(o,{class:"text-sm font-semibold text-green-500",icon:"arrow-down","aria-hidden":"true"}),t("li",S,[e[8]||(e[8]=t("p",{class:"mb-8 text-sm"}," Navigate to your Entra ID login customisation page. ",-1)),n(s,{variant:"secondary",class:"inline-block",target:"_blank",href:"https://entra.microsoft.com/#view/Microsoft_AAD_UsersAndTenants/CompanyBrandingWizard.ReactView/isDefault~/true/companyBrandingToEdit~/%7B%22id%22%3A%220%22%2C%22backgroundColor%22%3A%22%2340c223%22%2C%22backgroundImageRelativeUrl%22%3Anull%2C%22bannerLogoRelativeUrl%22%3Anull%2C%22cdnList%22%3A%5B%22aadcdn.msftauthimages.net%22%2C%22aadcdn.msauthimages.net%22%5D%2C%22customAccountResetCredentialsUrl%22%3Anull%2C%22customCannotAccessYourAccountText%22%3Anull%2C%22customCannotAccessYourAccountUrl%22%3Anull%2C%22customForgotMyPasswordText%22%3Anull%2C%22customPrivacyAndCookiesText%22%3Anull%2C%22customPrivacyAndCookiesUrl%22%3Anull%2C%22customResetItNowText%22%3Anull%2C%22customTermsOfUseText%22%3Anull%2C%22customTermsOfUseUrl%22%3Anull%2C%22faviconRelativeUrl%22%3Anull%2C%22customCSSRelativeUrl%22%3Anull%2C%22headerBackgroundColor%22%3Anull%2C%22signInPageText%22%3A%22%22%2C%22squareLogoRelativeUrl%22%3Anull%2C%22squareLogoDarkRelativeUrl%22%3Anull%2C%22usernameHintText%22%3A%22%22%2C%22headerLogoRelativeUrl%22%3Anull%2C%22loginPageTextVisibilitySettings%22%3A%7B%22hideCannotAccessYourAccount%22%3Anull%2C%22hideAccountResetCredentials%22%3Afalse%2C%22hideTermsOfUse%22%3Afalse%2C%22hidePrivacyAndCookies%22%3Afalse%2C%22hideForgotMyPassword%22%3Anull%2C%22hideResetItNow%22%3Anull%7D%2C%22contentCustomization%22%3A%7B%22adminConsentRelativeUrl%22%3Anull%2C%22attributeCollectionRelativeUrl%22%3Anull%2C%22registrationCampaignRelativeUrl%22%3Anull%2C%22conditionalAccessRelativeUrl%22%3Anull%2C%22adminConsent%22%3A%5B%5D%2C%22attributeCollection%22%3A%5B%5D%2C%22registrationCampaign%22%3A%5B%5D%2C%22conditionalAccess%22%3A%5B%5D%7D%2C%22loginPageLayoutConfiguration%22%3A%7B%22layoutTemplateType%22%3A%22default%22%2C%22isHeaderShown%22%3Afalse%2C%22isFooterShown%22%3Atrue%7D%7D/configuredLocales~/%5B%22en-US%22%5D"},{default:g(()=>e[7]||(e[7]=[u("Go to your page")])),_:1})]),n(o,{class:"text-sm font-semibold text-green-500",icon:"arrow-down","aria-hidden":"true"}),e[9]||(e[9]=v('<li class="py-16 bg-white rounded-lg"><p class="p-16 text-sm"> Choose <span class="font-bold">Layout</span>, scroll down to <span class="font-bold">Custom CSS</span>, click <span class="font-bold">Browse</span> and choose the downloaded CSS from the first step. </p></li>',1))])])])):C("",!0)],64)}}});export{N as _};
