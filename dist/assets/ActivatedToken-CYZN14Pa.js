import{d as i,r as m,o as l,a as p,q as a,m as k,N as c,B as d}from"./index-J02tC-VD.js";import{_}from"./TokenDisplay.vue_vue_type_script_setup_true_lang-D9p1cHp5.js";const g=i({__name:"ActivatedToken",props:{tokenData:{}},emits:["howToUse"],setup(o){const t=o,n=m({qrcode_png:t.tokenData.qrcode_png||"",token:t.tokenData.token||"",auth:t.tokenData.auth_token||""});return(s,e)=>{const r=d;return l(),p(c,null,[a(_,{"token-data":n.value},null,8,["token-data"]),a(r,{class:"mt-24",variant:"info",message:"When someone scans the QR Code with a reader, it will trigger the URL tied to your token and fire an alert.","text-link":"More tips?",onClick:e[0]||(e[0]=()=>s.$emit("howToUse"))}),e[1]||(e[1]=k("p",{class:"mt-24 text-sm"},null,-1))],64)}}});export{g as default};
