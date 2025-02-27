import{d as c,r as m,a as d,c as g,i as a,f as e,u as o,g as r,I as _,p as f}from"./index-BwEl8Aoe.js";import{_ as u}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-BXOcCbMI.js";import"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-BdHVwrN6.js";import"./BaseCopyButton-ddoXOfOr.js";const h={class:"flex flex-row items-center justify-center gap-16 mt-16"},k={href:"https://apps.apple.com/us/app/wireguard/id1441195209?itsct=apps_box_badge&itscg=30200",target:"_blank"},w=["src"],v={href:"https://play.google.com/store/apps/details?id=com.wireguard.android",target:"_blank"},x=["src"],W=c({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(n){const s=n,i=m({qr_code:s.tokenData.qr_code||"",wg_conf:s.tokenData.wg_conf||""});return(p,t)=>{const l=f;return d(),g(_,null,[a(u,{"token-data":i.value},null,8,["token-data"]),t[1]||(t[1]=e("p",{class:"mt-24 text-sm"}," Whenever someone tries to use this WireGuard VPN config to see what access it gets them, an alert is triggered. ",-1)),a(l,{class:"mt-24",variant:"info",message:"This WireGuard config can be installed anywhere WireGuard is used, such as on phones, laptops and servers.","text-link":"More tips?",onClick:t[0]||(t[0]=()=>p.$emit("howToUse"))}),t[2]||(t[2]=e("p",{class:"mt-24 text-center"},"Don't have the WireGuard app?",-1)),e("div",h,[e("a",k,[e("img",{src:o(r)("app-store.svg"),alt:"Download form Apple store",class:"h-[3rem]"},null,8,w)]),e("a",v,[e("img",{src:o(r)("google-play.png"),alt:"Download form Google Play store",class:"h-[3rem]"},null,8,x)])])],64)}}});export{W as default};
