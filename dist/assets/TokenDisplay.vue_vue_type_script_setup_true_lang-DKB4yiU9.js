import{d as _,r as d,a as i,c as u,f,i as k,j as m,h as D,q as g}from"./index-BWqoNE0f.js";const q={class:"flex flex-col items-center"},v=["src"],x=_({__name:"TokenDisplay",props:{tokenData:{}},setup(r){var s,c;const o=r,t=d(`${(s=o.tokenData)==null?void 0:s.token}.png`),a=d((c=o.tokenData)==null?void 0:c.qrcode_png);function l(){var n,e;a.value=`${(n=o.tokenData)==null?void 0:n.token}.png`,t.value=(e=o.tokenData)==null?void 0:e.qrcode_png}return(n,e)=>{const p=g;return i(),u("div",q,[f("img",{id:"qrcode_png",src:n.tokenData.qrcode_png,alt:"qrcode"},null,8,v),k(p,{class:"mt-16",href:t.value,download:a.value,onClick:e[0]||(e[0]=w=>l())},{default:m(()=>e[1]||(e[1]=[D("Download QR code")])),_:1},8,["href","download"])])}}});export{x as _};
