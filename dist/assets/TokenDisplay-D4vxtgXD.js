import{_ as b}from"./BaseCodeSnippet.vue_vue_type_script_setup_true_lang-DZf5eRC9.js";import{_ as w}from"./BaseCopyButton-CHEgU_jO.js";import{d as g,r as _,a as y,c as h,f as e,h as s,E as p,i,u as a,I as k,y as f}from"./index-oMzHRwJc.js";function D(r){var l;return`# Run the next line once to save the credentials:
cmdkey /generic:${(l=r.webdav_server)==null?void 0:l.split("/")[2]} /user:user /pass:${r.webdav_password}

# On each boot run the line below in a startup script:
net use * ${r.webdav_server} /savecred`}function x(r){var t;const o=(t=r.webdav_server)==null?void 0:t.split("/")[2];return"https://user:"+r.webdav_password+"@"+o}const O={class:"relative bg-white border rounded-2xl border-grey-100"},S={class:"relative bg-white border rounded-2xl border-grey-100 mr-2.5rem]"},C={id:"input-wrapper"},B=["value"],V=g({__name:"TokenDisplay",props:{tokenData:{}},setup(r){const o=r,t=_({hostname:o.tokenData.hostname,webdav_fs_type:o.tokenData.webdav_fs_type,webdav_password:o.tokenData.webdav_password,webdav_server:o.tokenData.webdav_server}),l=D(t.value),u=x(t.value),v=t.value.webdav_server?t.value.webdav_server:"error",m=t.value.webdav_password?t.value.webdav_password:"error";return(W,n)=>{const d=w,c=b;return y(),h(k,null,[e("div",null,[n[3]||(n[3]=e("label",{class:"mt-16 mb-8 text-grey-500 inline-block"},"Here are the generic parameters:",-1)),e("div",O,[e("ul",null,[e("li",null,[n[0]||(n[0]=s("WebDAV server: ")),e("strong",null,p(t.value.webdav_server),1),i(d,{content:a(v),class:"ring-white ring-4 ml-8"},null,8,["content"])]),n[2]||(n[2]=e("li",null,[s("Username: Pick anything (e.g. "),e("strong",null,"service"),s(", "),e("strong",null,"Sabrina"),s(", or "),e("strong",null,"Admin"),s(")")],-1)),e("li",null,[n[1]||(n[1]=s("Password: ")),e("strong",null,p(t.value.webdav_password),1),i(d,{content:a(m),class:"ring-white ring-4 ml-8"},null,8,["content"])])])])]),n[9]||(n[9]=e("label",{class:"mt-16 mb-8 text-grey-500 inline-block"},[s("On "),e("strong",null,"Windows"),s(" systems, run these commands in cmd.exe:")],-1)),i(c,{lang:"shell",code:a(l),"custom-height":"9.5rem"},null,8,["code"]),e("div",null,[n[8]||(n[8]=e("label",{class:"mt-16 mb-8 text-grey-500 inline-block"},[s("On "),e("strong",null,"MacOS"),s(" systems, configure a Network Folder with these steps:")],-1)),e("div",S,[e("ul",null,[n[6]||(n[6]=e("li",null,"Open the Finder, then type ⌘-K to Connect to Server.",-1)),e("li",null,[n[4]||(n[4]=s("Copy and paste ")),e("span",C,[e("input",{class:"w-[12rem]",value:a(u)},null,8,B),i(d,{content:a(u),class:"ring-white ring-4"},null,8,["content"])]),n[5]||(n[5]=s(" as the hostname, then click Connect."))]),n[7]||(n[7]=e("li",null,`Alternatively, to automatically mount the folder at login, use the "WebDAV server" field above as the hostname, then enter the username and password and check "Remember this password in my Keychain". Open System Settings -> General -> Open at Login, click the '+' to add a new item, navigate to the newly-mounted folder, and select it, then click Open.`,-1))])])])],64)}}}),N=f(V,[["__scopeId","data-v-a8b4a94b"]]);export{N as T};