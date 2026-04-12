import{af as ae,m as S,aF as ce,d as A,n as C,p as le,q as P,s as j,v as R,x as b,I as Q,o as ne,w as J,J as W,O as oe,r as D,W as O,at as ue,a8 as me,L as fe,aB as se,a6 as he,aj as pe,Q as F,av as ge,ab as ve,ad as xe,aG as be,aH as X,a9 as Ce,aI as we,aJ as ye,ai as $e,ay as Ne,ak as _e,aK as ee,l as B,b as h,u,N as je,Y as H,f as Re,a as g,k as N,t as T,j as te,c as Se,Z as ze,F as Ee,B as re,g as Pe,h as k}from"./index-DCBkkiSD.js";import{r as K}from"./recordings-DyheRC-V.js";import{f as Ie}from"./time-DBiNR5Lf.js";import{N as Z}from"./Divider-CtHy420i.js";import{u as Te}from"./use-message-DhCh5Tkl.js";import{N as E,a as ke}from"./DescriptionsItem-qj6gyjzC.js";import{N as De}from"./DynamicTags-CXj4WGnK.js";import{N as Ae}from"./Tag-Bv7Q4RGz.js";import"./client-DofY_RJ9.js";import"./Input-Bv6o2VYU.js";import"./Add-Dx_620QU.js";function Le(t,e){const s=ae(ce,null);return S(()=>t.hljs||(s==null?void 0:s.mergedHljsRef.value))}const Be=A({name:"ChevronLeft",render(){return C("svg",{viewBox:"0 0 16 16",fill:"none",xmlns:"http://www.w3.org/2000/svg"},C("path",{d:"M10.3536 3.14645C10.5488 3.34171 10.5488 3.65829 10.3536 3.85355L6.20711 8L10.3536 12.1464C10.5488 12.3417 10.5488 12.6583 10.3536 12.8536C10.1583 13.0488 9.84171 13.0488 9.64645 12.8536L5.14645 8.35355C4.95118 8.15829 4.95118 7.84171 5.14645 7.64645L9.64645 3.14645C9.84171 2.95118 10.1583 2.95118 10.3536 3.14645Z",fill:"currentColor"}))}});function Fe(t){const{textColor2:e,fontSize:s,fontWeightStrong:i,textColor3:r}=t;return{textColor:e,fontSize:s,fontWeightStrong:i,"mono-3":"#a0a1a7","hue-1":"#0184bb","hue-2":"#4078f2","hue-3":"#a626a4","hue-4":"#50a14f","hue-5":"#e45649","hue-5-2":"#c91243","hue-6":"#986801","hue-6-2":"#c18401",lineNumberTextColor:r}}const He={common:le,self:Fe},Oe=P([j("code",`
 font-size: var(--n-font-size);
 font-family: var(--n-font-family);
 `,[R("show-line-numbers",`
 display: flex;
 `),b("line-numbers",`
 user-select: none;
 padding-right: 12px;
 text-align: right;
 transition: color .3s var(--n-bezier);
 color: var(--n-line-number-text-color);
 `),R("word-wrap",[P("pre",`
 white-space: pre-wrap;
 word-break: break-all;
 `)]),P("pre",`
 margin: 0;
 line-height: inherit;
 font-size: inherit;
 font-family: inherit;
 `),P("[class^=hljs]",`
 color: var(--n-text-color);
 transition: 
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `)]),({props:t})=>{const e=`${t.bPrefix}code`;return[`${e} .hljs-comment,
 ${e} .hljs-quote {
 color: var(--n-mono-3);
 font-style: italic;
 }`,`${e} .hljs-doctag,
 ${e} .hljs-keyword,
 ${e} .hljs-formula {
 color: var(--n-hue-3);
 }`,`${e} .hljs-section,
 ${e} .hljs-name,
 ${e} .hljs-selector-tag,
 ${e} .hljs-deletion,
 ${e} .hljs-subst {
 color: var(--n-hue-5);
 }`,`${e} .hljs-literal {
 color: var(--n-hue-1);
 }`,`${e} .hljs-string,
 ${e} .hljs-regexp,
 ${e} .hljs-addition,
 ${e} .hljs-attribute,
 ${e} .hljs-meta-string {
 color: var(--n-hue-4);
 }`,`${e} .hljs-built_in,
 ${e} .hljs-class .hljs-title {
 color: var(--n-hue-6-2);
 }`,`${e} .hljs-attr,
 ${e} .hljs-variable,
 ${e} .hljs-template-variable,
 ${e} .hljs-type,
 ${e} .hljs-selector-class,
 ${e} .hljs-selector-attr,
 ${e} .hljs-selector-pseudo,
 ${e} .hljs-number {
 color: var(--n-hue-6);
 }`,`${e} .hljs-symbol,
 ${e} .hljs-bullet,
 ${e} .hljs-link,
 ${e} .hljs-meta,
 ${e} .hljs-selector-id,
 ${e} .hljs-title {
 color: var(--n-hue-2);
 }`,`${e} .hljs-emphasis {
 font-style: italic;
 }`,`${e} .hljs-strong {
 font-weight: var(--n-font-weight-strong);
 }`,`${e} .hljs-link {
 text-decoration: underline;
 }`]}]),We=Object.assign(Object.assign({},W.props),{language:String,code:{type:String,default:""},trim:{type:Boolean,default:!0},hljs:Object,uri:Boolean,inline:Boolean,wordWrap:Boolean,showLineNumbers:Boolean,internalFontSize:Number,internalNoHighlight:Boolean}),G=A({name:"Code",props:We,setup(t,{slots:e}){const{internalNoHighlight:s}=t,{mergedClsPrefixRef:i,inlineThemeDisabled:r}=Q(),n=D(null),p=s?{value:void 0}:Le(t),w=(d,f,c)=>{const{value:o}=p;return!o||!(d&&o.getLanguage(d))?null:o.highlight(c?f.trim():f,{language:d}).value},_=S(()=>t.inline||t.wordWrap?!1:t.showLineNumbers),v=()=>{if(e.default)return;const{value:d}=n;if(!d)return;const{language:f}=t,c=t.uri?window.decodeURIComponent(t.code):t.code;if(f){const m=w(f,c,t.trim);if(m!==null){if(t.inline)d.innerHTML=m;else{const x=d.querySelector(".__code__");x&&d.removeChild(x);const $=document.createElement("pre");$.className="__code__",$.innerHTML=m,d.appendChild($)}return}}if(t.inline){d.textContent=c;return}const o=d.querySelector(".__code__");if(o)o.textContent=c;else{const m=document.createElement("pre");m.className="__code__",m.textContent=c,d.innerHTML="",d.appendChild(m)}};ne(v),J(O(t,"language"),v),J(O(t,"code"),v),s||J(p,v);const y=W("Code","-code",Oe,He,t,i),l=S(()=>{const{common:{cubicBezierEaseInOut:d,fontFamilyMono:f},self:{textColor:c,fontSize:o,fontWeightStrong:m,lineNumberTextColor:x,"mono-3":$,"hue-1":z,"hue-2":I,"hue-3":L,"hue-4":M,"hue-5":U,"hue-5-2":V,"hue-6":q,"hue-6-2":de}}=y.value,{internalFontSize:Y}=t;return{"--n-font-size":Y?`${Y}px`:o,"--n-font-family":f,"--n-font-weight-strong":m,"--n-bezier":d,"--n-text-color":c,"--n-mono-3":$,"--n-hue-1":z,"--n-hue-2":I,"--n-hue-3":L,"--n-hue-4":M,"--n-hue-5":U,"--n-hue-5-2":V,"--n-hue-6":q,"--n-hue-6-2":de,"--n-line-number-text-color":x}}),a=r?oe("code",S(()=>`${t.internalFontSize||"a"}`),l,t):void 0;return{mergedClsPrefix:i,codeRef:n,mergedShowLineNumbers:_,lineNumbers:S(()=>{let d=1;const f=[];let c=!1;for(const o of t.code)o===`
`?(c=!0,f.push(d++)):c=!1;return c||f.push(d++),f.join(`
`)}),cssVars:r?void 0:l,themeClass:a==null?void 0:a.themeClass,onRender:a==null?void 0:a.onRender}},render(){var t,e;const{mergedClsPrefix:s,wordWrap:i,mergedShowLineNumbers:r,onRender:n}=this;return n==null||n(),C("code",{class:[`${s}-code`,this.themeClass,i&&`${s}-code--word-wrap`,r&&`${s}-code--show-line-numbers`],style:this.cssVars,ref:"codeRef"},r?C("pre",{class:`${s}-code__line-numbers`},this.lineNumbers):null,(e=(t=this.$slots).default)===null||e===void 0?void 0:e.call(t))}});function Me(t){const{fontWeight:e,textColor1:s,textColor2:i,textColorDisabled:r,dividerColor:n,fontSize:p}=t;return{titleFontSize:p,titleFontWeight:e,dividerColor:n,titleTextColor:s,titleTextColorDisabled:r,fontSize:p,textColor:i,arrowColor:i,arrowColorDisabled:r,itemMargin:"16px 0 0 0",titlePadding:"16px 0 0 0"}}const Ue={common:le,self:Me},Ve=j("collapse","width: 100%;",[j("collapse-item",`
 font-size: var(--n-font-size);
 color: var(--n-text-color);
 transition:
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 margin: var(--n-item-margin);
 `,[R("disabled",[b("header","cursor: not-allowed;",[b("header-main",`
 color: var(--n-title-text-color-disabled);
 `),j("collapse-item-arrow",`
 color: var(--n-arrow-color-disabled);
 `)])]),j("collapse-item","margin-left: 32px;"),P("&:first-child","margin-top: 0;"),P("&:first-child >",[b("header","padding-top: 0;")]),R("left-arrow-placement",[b("header",[j("collapse-item-arrow","margin-right: 4px;")])]),R("right-arrow-placement",[b("header",[j("collapse-item-arrow","margin-left: 4px;")])]),b("content-wrapper",[b("content-inner","padding-top: 16px;"),ue({duration:"0.15s"})]),R("active",[b("header",[R("active",[j("collapse-item-arrow","transform: rotate(90deg);")])])]),P("&:not(:first-child)","border-top: 1px solid var(--n-divider-color);"),me("disabled",[R("trigger-area-main",[b("header",[b("header-main","cursor: pointer;"),j("collapse-item-arrow","cursor: default;")])]),R("trigger-area-arrow",[b("header",[j("collapse-item-arrow","cursor: pointer;")])]),R("trigger-area-extra",[b("header",[b("header-extra","cursor: pointer;")])])]),b("header",`
 font-size: var(--n-title-font-size);
 display: flex;
 flex-wrap: nowrap;
 align-items: center;
 transition: color .3s var(--n-bezier);
 position: relative;
 padding: var(--n-title-padding);
 color: var(--n-title-text-color);
 `,[b("header-main",`
 display: flex;
 flex-wrap: nowrap;
 align-items: center;
 font-weight: var(--n-title-font-weight);
 transition: color .3s var(--n-bezier);
 flex: 1;
 color: var(--n-title-text-color);
 `),b("header-extra",`
 display: flex;
 align-items: center;
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 `),j("collapse-item-arrow",`
 display: flex;
 transition:
 transform .15s var(--n-bezier),
 color .3s var(--n-bezier);
 font-size: 18px;
 color: var(--n-arrow-color);
 `)])])]),qe=Object.assign(Object.assign({},W.props),{defaultExpandedNames:{type:[Array,String],default:null},expandedNames:[Array,String],arrowPlacement:{type:String,default:"left"},accordion:{type:Boolean,default:!1},displayDirective:{type:String,default:"if"},triggerAreas:{type:Array,default:()=>["main","extra","arrow"]},onItemHeaderClick:[Function,Array],"onUpdate:expandedNames":[Function,Array],onUpdateExpandedNames:[Function,Array],onExpandedNamesChange:{type:[Function,Array],validator:()=>!0,default:void 0}}),ie=he("n-collapse"),Je=A({name:"Collapse",props:qe,slots:Object,setup(t,{slots:e}){const{mergedClsPrefixRef:s,inlineThemeDisabled:i,mergedRtlRef:r}=Q(t),n=D(t.defaultExpandedNames),p=S(()=>t.expandedNames),w=fe(p,n),_=W("Collapse","-collapse",Ve,Ue,t,s);function v(c){const{"onUpdate:expandedNames":o,onUpdateExpandedNames:m,onExpandedNamesChange:x}=t;m&&F(m,c),o&&F(o,c),x&&F(x,c),n.value=c}function y(c){const{onItemHeaderClick:o}=t;o&&F(o,c)}function l(c,o,m){const{accordion:x}=t,{value:$}=w;if(x)c?(v([o]),y({name:o,expanded:!0,event:m})):(v([]),y({name:o,expanded:!1,event:m}));else if(!Array.isArray($))v([o]),y({name:o,expanded:!0,event:m});else{const z=$.slice(),I=z.findIndex(L=>o===L);~I?(z.splice(I,1),v(z),y({name:o,expanded:!1,event:m})):(z.push(o),v(z),y({name:o,expanded:!0,event:m}))}}pe(ie,{props:t,mergedClsPrefixRef:s,expandedNamesRef:w,slots:e,toggleItem:l});const a=se("Collapse",r,s),d=S(()=>{const{common:{cubicBezierEaseInOut:c},self:{titleFontWeight:o,dividerColor:m,titlePadding:x,titleTextColor:$,titleTextColorDisabled:z,textColor:I,arrowColor:L,fontSize:M,titleFontSize:U,arrowColorDisabled:V,itemMargin:q}}=_.value;return{"--n-font-size":M,"--n-bezier":c,"--n-text-color":I,"--n-divider-color":m,"--n-title-padding":x,"--n-title-font-size":U,"--n-title-text-color":$,"--n-title-text-color-disabled":z,"--n-title-font-weight":o,"--n-arrow-color":L,"--n-arrow-color-disabled":V,"--n-item-margin":q}}),f=i?oe("collapse",void 0,d,t):void 0;return{rtlEnabled:a,mergedTheme:_,mergedClsPrefix:s,cssVars:i?void 0:d,themeClass:f==null?void 0:f.themeClass,onRender:f==null?void 0:f.onRender}},render(){var t;return(t=this.onRender)===null||t===void 0||t.call(this),C("div",{class:[`${this.mergedClsPrefix}-collapse`,this.rtlEnabled&&`${this.mergedClsPrefix}-collapse--rtl`,this.themeClass],style:this.cssVars},this.$slots)}}),Ke=A({name:"CollapseItemContent",props:{displayDirective:{type:String,required:!0},show:Boolean,clsPrefix:{type:String,required:!0}},setup(t){return{onceTrue:be(O(t,"show"))}},render(){return C(ge,null,{default:()=>{const{show:t,displayDirective:e,onceTrue:s,clsPrefix:i}=this,r=e==="show"&&s,n=C("div",{class:`${i}-collapse-item__content-wrapper`},C("div",{class:`${i}-collapse-item__content-inner`},this.$slots));return r?ve(n,[[xe,t]]):t?n:null}})}}),Ze={title:String,name:[String,Number],disabled:Boolean,displayDirective:String},Ge=A({name:"CollapseItem",props:Ze,setup(t){const{mergedRtlRef:e}=Q(t),s=$e(),i=Ne(()=>{var l;return(l=t.name)!==null&&l!==void 0?l:s}),r=ae(ie);r||_e("collapse-item","`n-collapse-item` must be placed inside `n-collapse`.");const{expandedNamesRef:n,props:p,mergedClsPrefixRef:w,slots:_}=r,v=S(()=>{const{value:l}=n;if(Array.isArray(l)){const{value:a}=i;return!~l.findIndex(d=>d===a)}else if(l){const{value:a}=i;return a!==l}return!0});return{rtlEnabled:se("Collapse",e,w),collapseSlots:_,randomName:s,mergedClsPrefix:w,collapsed:v,triggerAreas:O(p,"triggerAreas"),mergedDisplayDirective:S(()=>{const{displayDirective:l}=t;return l||p.displayDirective}),arrowPlacement:S(()=>p.arrowPlacement),handleClick(l){let a="main";ee(l,"arrow")&&(a="arrow"),ee(l,"extra")&&(a="extra"),p.triggerAreas.includes(a)&&r&&!t.disabled&&r.toggleItem(v.value,i.value,l)}}},render(){const{collapseSlots:t,$slots:e,arrowPlacement:s,collapsed:i,mergedDisplayDirective:r,mergedClsPrefix:n,disabled:p,triggerAreas:w}=this,_=X(e.header,{collapsed:i},()=>[this.title]),v=e["header-extra"]||t["header-extra"],y=e.arrow||t.arrow;return C("div",{class:[`${n}-collapse-item`,`${n}-collapse-item--${s}-arrow-placement`,p&&`${n}-collapse-item--disabled`,!i&&`${n}-collapse-item--active`,w.map(l=>`${n}-collapse-item--trigger-area-${l}`)]},C("div",{class:[`${n}-collapse-item__header`,!i&&`${n}-collapse-item__header--active`]},C("div",{class:`${n}-collapse-item__header-main`,onClick:this.handleClick},s==="right"&&_,C("div",{class:`${n}-collapse-item-arrow`,key:this.rtlEnabled?0:1,"data-arrow":!0},X(y,{collapsed:i},()=>[C(Ce,{clsPrefix:n},{default:()=>this.rtlEnabled?C(Be,null):C(we,null)})])),s==="left"&&_),ye(v,{collapsed:i},l=>C("div",{class:`${n}-collapse-item__header-extra`,onClick:this.handleClick,"data-extra":!0},l))),C(Ke,{clsPrefix:n,displayDirective:r,show:!i},e))}}),it=A({__name:"RecordingDetail",setup(t){const e=Re(),s=Pe(),i=Te(),r=D(null),n=D(!1),p=D(!1),w=D([]);async function _(l){if(r.value){p.value=!0;try{const a=await K.updateTags(r.value.id,l);r.value=a.data,i.success("标签已保存")}catch{i.error("保存失败")}finally{p.value=!1}}}async function v(){var l,a;n.value=!0;try{const d=await K.recapture(e.params.id);r.value=d.data,i.success("基线响应已更新")}catch(d){i.error(((a=(l=d.response)==null?void 0:l.data)==null?void 0:a.detail)||"捕获失败")}finally{n.value=!1}}function y(l){if(!l)return"";try{return JSON.stringify(JSON.parse(l),null,2)}catch{return l}}return ne(async()=>{const l=await K.get(e.params.id);r.value=l.data,w.value=l.data.tags||[]}),(l,a)=>{var d,f,c;return r.value?(k(),B(u(je),{key:0,title:`录制详情 — ${((d=r.value)==null?void 0:d.entry_type)||""} ${((f=r.value)==null?void 0:f.host)||""} ${((c=r.value)==null?void 0:c.path)||""}`},{"header-extra":h(()=>[g(u(te),null,{default:h(()=>[g(u(re),{size:"small",loading:n.value,onClick:v},{default:h(()=>[...a[2]||(a[2]=[N("重新捕获基线",-1)])]),_:1},8,["loading"]),g(u(re),{size:"small",onClick:a[0]||(a[0]=o=>u(s).back())},{default:h(()=>[...a[3]||(a[3]=[N("返回",-1)])]),_:1})]),_:1})]),default:h(()=>{var o,m;return[g(u(ke),{bordered:"",column:2},{default:h(()=>[g(u(E),{label:"TraceId"},{default:h(()=>[N(T(r.value.trace_id||"-"),1)]),_:1}),g(u(E),{label:"应用"},{default:h(()=>[N(T(r.value.entry_app||"-"),1)]),_:1}),g(u(E),{label:"Host"},{default:h(()=>[N(T(r.value.host||"-"),1)]),_:1}),g(u(E),{label:"耗时"},{default:h(()=>[N(T(r.value.duration_ms?r.value.duration_ms+"ms":"-"),1)]),_:1}),g(u(E),{label:"时间"},{default:h(()=>[N(T(u(Ie)(r.value.timestamp||r.value.created_at)),1)]),_:1}),g(u(E),{label:"状态"},{default:h(()=>[N(T({PASS:"通过",FAIL:"失败",ERROR:"错误",PARSED:"已解析",RAW:"原始",ADDED_TO_CASE:"已加入用例"}[r.value.status]||r.value.status),1)]),_:1}),g(u(E),{label:"标签",span:2},{default:h(()=>[g(u(te),{align:"center"},{default:h(()=>[g(u(De),{value:w.value,"onUpdate:value":[a[1]||(a[1]=x=>w.value=x),_]},null,8,["value"]),p.value?(k(),B(u(Ae),{key:0,size:"small",type:"info"},{default:h(()=>[...a[4]||(a[4]=[N("保存中…",-1)])]),_:1})):H("",!0)]),_:1})]),_:1})]),_:1}),g(u(Z),null,{default:h(()=>[...a[5]||(a[5]=[N("请求报文",-1)])]),_:1}),g(u(G),{code:y(r.value.request_body),language:"json","show-line-numbers":""},null,8,["code"]),g(u(Z),null,{default:h(()=>[...a[6]||(a[6]=[N("响应报文",-1)])]),_:1}),g(u(G),{code:y(r.value.response_body),language:"json","show-line-numbers":""},null,8,["code"]),(o=r.value.sub_invocations)!=null&&o.length?(k(),B(u(Z),{key:0},{default:h(()=>[...a[7]||(a[7]=[N("子调用 (Mock)",-1)])]),_:1})):H("",!0),(m=r.value.sub_invocations)!=null&&m.length?(k(),B(u(Je),{key:1},{default:h(()=>[(k(!0),Se(Ee,null,ze(r.value.sub_invocations,(x,$)=>(k(),B(u(Ge),{key:$,title:`Sub #${$+1} — ${x.type||x.invokeType||"UNKNOWN"}`},{default:h(()=>[g(u(G),{code:JSON.stringify(x,null,2),language:"json","show-line-numbers":""},null,8,["code"])]),_:2},1032,["title"]))),128))]),_:1})):H("",!0)]}),_:1},8,["title"])):H("",!0)}}});export{it as default};
