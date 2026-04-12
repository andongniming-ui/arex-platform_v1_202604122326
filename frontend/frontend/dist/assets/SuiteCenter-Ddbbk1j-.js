import{d as pe,n as h,bc as Ot,r as w,bd as Ht,be as Ge,bf as Dt,bg as we,bh as Gt,p as Ut,a6 as qt,ak as Xt,af as it,aT as Qt,F as st,a9 as Yt,bi as Kt,b1 as Jt,m as de,bj as Zt,s as i,v,q as E,x as F,a8 as ea,bk as We,b8 as Ue,bl as Ae,I as ta,J as dt,L as aa,w as Se,o as ut,bm as ra,al as na,O as la,bn as qe,bb as oa,ab as ia,ad as sa,bo as da,bp as ua,U as Ee,as as Y,bq as xe,aj as ca,W as K,Q as ye,l as Ie,b as m,u as s,j as be,f as ba,a as c,i as Ne,t as je,B as J,k as X,N as Xe,c as fa,Z as pa,Y as va,e as ga,X as Qe,g as ma,h as _e}from"./index-DCBkkiSD.js";import{c as Z}from"./client-DofY_RJ9.js";import{a as ha}from"./applications-WwaMyD6G.js";import{t as xa}from"./testCases-DhwkMiAa.js";import{f as Ye}from"./time-DBiNR5Lf.js";import{c as ya,i as _a}from"./dateRange-BwFEbxrI.js";import{g as Ke,a as Ca,s as Je,b as Sa}from"./filterQuery-CNr8cEn4.js";import{A as wa}from"./Add-Dx_620QU.js";import{u as Ta}from"./use-message-DhCh5Tkl.js";import{N as Ze}from"./DataTable-DwNW1pWN.js";import{N as se}from"./Input-Bv6o2VYU.js";import{N as Ce}from"./Select-eTh6aqH5.js";import{N as za}from"./DatePicker-Bn103OX4.js";import{N as et}from"./Form-BPvxXi5g.js";import{N as D}from"./FormItem-BoZw6hrU.js";import{N as fe}from"./InputNumber-_tEWDElD.js";import{N as Ra}from"./Divider-CtHy420i.js";import{N as Pa}from"./Popconfirm-Cg2Mqybt.js";import{N as $a}from"./Tag-Bv7Q4RGz.js";const La=Ge(".v-x-scroll",{overflow:"auto",scrollbarWidth:"none"},[Ge("&::-webkit-scrollbar",{width:0,height:0})]),ka=pe({name:"XScroll",props:{disabled:Boolean,onScroll:Function},setup(){const e=w(null);function o(b){!(b.currentTarget.offsetWidth<b.currentTarget.scrollWidth)||b.deltaY===0||(b.currentTarget.scrollLeft+=b.deltaY+b.deltaX,b.preventDefault())}const f=Ht();return La.mount({id:"vueuc/x-scroll",head:!0,anchorMetaName:Ot,ssr:f}),Object.assign({selfRef:e,handleWheel:o},{scrollTo(...b){var P;(P=e.value)===null||P===void 0||P.scrollTo(...b)}})},render(){return h("div",{ref:"selfRef",onScroll:this.onScroll,onWheel:this.disabled?void 0:this.handleWheel,class:"v-x-scroll"},this.$slots)}});var Ba=/\s/;function Wa(e){for(var o=e.length;o--&&Ba.test(e.charAt(o)););return o}var Aa=/^\s+/;function Ea(e){return e&&e.slice(0,Wa(e)+1).replace(Aa,"")}var tt=NaN,Ia=/^[-+]0x[0-9a-f]+$/i,Na=/^0b[01]+$/i,ja=/^0o[0-7]+$/i,Ma=parseInt;function at(e){if(typeof e=="number")return e;if(Dt(e))return tt;if(we(e)){var o=typeof e.valueOf=="function"?e.valueOf():e;e=we(o)?o+"":o}if(typeof e!="string")return e===0?e:+e;e=Ea(e);var f=Na.test(e);return f||ja.test(e)?Ma(e.slice(2),f?2:8):Ia.test(e)?tt:+e}var Me=function(){return Gt.Date.now()},Va="Expected a function",Fa=Math.max,Oa=Math.min;function Ha(e,o,f){var p,b,P,u,S,T,R=0,$=!1,B=!1,W=!0;if(typeof e!="function")throw new TypeError(Va);o=at(o)||0,we(f)&&($=!!f.leading,B="maxWait"in f,P=B?Fa(at(f.maxWait)||0,o):P,W="trailing"in f?!!f.trailing:W);function z(g){var V=p,G=b;return p=b=void 0,R=g,u=e.apply(G,V),u}function L(g){return R=g,S=setTimeout(y,o),$?z(g):u}function A(g){var V=g-T,G=g-R,H=o-V;return B?Oa(H,P-G):H}function I(g){var V=g-T,G=g-R;return T===void 0||V>=o||V<0||B&&G>=P}function y(){var g=Me();if(I(g))return _(g);S=setTimeout(y,A(g))}function _(g){return S=void 0,W&&p?z(g):(p=b=void 0,u)}function O(){S!==void 0&&clearTimeout(S),R=0,p=T=b=S=void 0}function M(){return S===void 0?u:_(Me())}function C(){var g=Me(),V=I(g);if(p=arguments,b=this,T=g,V){if(S===void 0)return L(T);if(B)return clearTimeout(S),S=setTimeout(y,o),z(T)}return S===void 0&&(S=setTimeout(y,o)),u}return C.cancel=O,C.flush=M,C}var Da="Expected a function";function Ga(e,o,f){var p=!0,b=!0;if(typeof e!="function")throw new TypeError(Da);return we(f)&&(p="leading"in f?!!f.leading:p,b="trailing"in f?!!f.trailing:b),Ha(e,o,{leading:p,maxWait:o,trailing:b})}const Ua={tabFontSizeSmall:"14px",tabFontSizeMedium:"14px",tabFontSizeLarge:"16px",tabGapSmallLine:"36px",tabGapMediumLine:"36px",tabGapLargeLine:"36px",tabGapSmallLineVertical:"8px",tabGapMediumLineVertical:"8px",tabGapLargeLineVertical:"8px",tabPaddingSmallLine:"6px 0",tabPaddingMediumLine:"10px 0",tabPaddingLargeLine:"14px 0",tabPaddingVerticalSmallLine:"6px 12px",tabPaddingVerticalMediumLine:"8px 16px",tabPaddingVerticalLargeLine:"10px 20px",tabGapSmallBar:"36px",tabGapMediumBar:"36px",tabGapLargeBar:"36px",tabGapSmallBarVertical:"8px",tabGapMediumBarVertical:"8px",tabGapLargeBarVertical:"8px",tabPaddingSmallBar:"4px 0",tabPaddingMediumBar:"6px 0",tabPaddingLargeBar:"10px 0",tabPaddingVerticalSmallBar:"6px 12px",tabPaddingVerticalMediumBar:"8px 16px",tabPaddingVerticalLargeBar:"10px 20px",tabGapSmallCard:"4px",tabGapMediumCard:"4px",tabGapLargeCard:"4px",tabGapSmallCardVertical:"4px",tabGapMediumCardVertical:"4px",tabGapLargeCardVertical:"4px",tabPaddingSmallCard:"8px 16px",tabPaddingMediumCard:"10px 20px",tabPaddingLargeCard:"12px 24px",tabPaddingSmallSegment:"4px 0",tabPaddingMediumSegment:"6px 0",tabPaddingLargeSegment:"8px 0",tabPaddingVerticalLargeSegment:"0 8px",tabPaddingVerticalSmallCard:"8px 12px",tabPaddingVerticalMediumCard:"10px 16px",tabPaddingVerticalLargeCard:"12px 20px",tabPaddingVerticalSmallSegment:"0 4px",tabPaddingVerticalMediumSegment:"0 6px",tabGapSmallSegment:"0",tabGapMediumSegment:"0",tabGapLargeSegment:"0",tabGapSmallSegmentVertical:"0",tabGapMediumSegmentVertical:"0",tabGapLargeSegmentVertical:"0",panePaddingSmall:"8px 0 0 0",panePaddingMedium:"12px 0 0 0",panePaddingLarge:"16px 0 0 0",closeSize:"18px",closeIconSize:"14px"};function qa(e){const{textColor2:o,primaryColor:f,textColorDisabled:p,closeIconColor:b,closeIconColorHover:P,closeIconColorPressed:u,closeColorHover:S,closeColorPressed:T,tabColor:R,baseColor:$,dividerColor:B,fontWeight:W,textColor1:z,borderRadius:L,fontSize:A,fontWeightStrong:I}=e;return Object.assign(Object.assign({},Ua),{colorSegment:R,tabFontSizeCard:A,tabTextColorLine:z,tabTextColorActiveLine:f,tabTextColorHoverLine:f,tabTextColorDisabledLine:p,tabTextColorSegment:z,tabTextColorActiveSegment:o,tabTextColorHoverSegment:o,tabTextColorDisabledSegment:p,tabTextColorBar:z,tabTextColorActiveBar:f,tabTextColorHoverBar:f,tabTextColorDisabledBar:p,tabTextColorCard:z,tabTextColorHoverCard:z,tabTextColorActiveCard:f,tabTextColorDisabledCard:p,barColor:f,closeIconColor:b,closeIconColorHover:P,closeIconColorPressed:u,closeColorHover:S,closeColorPressed:T,closeBorderRadius:L,tabColor:R,tabColorSegment:$,tabBorderColor:B,tabFontWeightActive:W,tabFontWeight:W,tabBorderRadius:L,paneTextColor:o,fontWeightStrong:I})}const Xa={common:Ut,self:qa},He=qt("n-tabs"),ct={tab:[String,Number,Object,Function],name:{type:[String,Number],required:!0},disabled:Boolean,displayDirective:{type:String,default:"if"},closable:{type:Boolean,default:void 0},tabProps:Object,label:[String,Number,Object,Function]},rt=pe({__TAB_PANE__:!0,name:"TabPane",alias:["TabPanel"],props:ct,slots:Object,setup(e){const o=it(He,null);return o||Xt("tab-pane","`n-tab-pane` must be placed inside `n-tabs`."),{style:o.paneStyleRef,class:o.paneClassRef,mergedClsPrefix:o.mergedClsPrefixRef}},render(){return h("div",{class:[`${this.mergedClsPrefix}-tab-pane`,this.class],style:this.style},this.$slots)}}),Qa=Object.assign({internalLeftPadded:Boolean,internalAddable:Boolean,internalCreatedByPane:Boolean},Zt(ct,["displayDirective"])),Oe=pe({__TAB__:!0,inheritAttrs:!1,name:"Tab",props:Qa,setup(e){const{mergedClsPrefixRef:o,valueRef:f,typeRef:p,closableRef:b,tabStyleRef:P,addTabStyleRef:u,tabClassRef:S,addTabClassRef:T,tabChangeIdRef:R,onBeforeLeaveRef:$,triggerRef:B,handleAdd:W,activateTab:z,handleClose:L}=it(He);return{trigger:B,mergedClosable:de(()=>{if(e.internalAddable)return!1;const{closable:A}=e;return A===void 0?b.value:A}),style:P,addStyle:u,tabClass:S,addTabClass:T,clsPrefix:o,value:f,type:p,handleClose(A){A.stopPropagation(),!e.disabled&&L(e.name)},activateTab(){if(e.disabled)return;if(e.internalAddable){W();return}const{name:A}=e,I=++R.id;if(A!==f.value){const{value:y}=$;y?Promise.resolve(y(e.name,f.value)).then(_=>{_&&R.id===I&&z(A)}):z(A)}}}},render(){const{internalAddable:e,clsPrefix:o,name:f,disabled:p,label:b,tab:P,value:u,mergedClosable:S,trigger:T,$slots:{default:R}}=this,$=b??P;return h("div",{class:`${o}-tabs-tab-wrapper`},this.internalLeftPadded?h("div",{class:`${o}-tabs-tab-pad`}):null,h("div",Object.assign({key:f,"data-name":f,"data-disabled":p?!0:void 0},Qt({class:[`${o}-tabs-tab`,u===f&&`${o}-tabs-tab--active`,p&&`${o}-tabs-tab--disabled`,S&&`${o}-tabs-tab--closable`,e&&`${o}-tabs-tab--addable`,e?this.addTabClass:this.tabClass],onClick:T==="click"?this.activateTab:void 0,onMouseenter:T==="hover"?this.activateTab:void 0,style:e?this.addStyle:this.style},this.internalCreatedByPane?this.tabProps||{}:this.$attrs)),h("span",{class:`${o}-tabs-tab__label`},e?h(st,null,h("div",{class:`${o}-tabs-tab__height-placeholder`}," "),h(Yt,{clsPrefix:o},{default:()=>h(wa,null)})):R?R():typeof $=="object"?$:Kt($??f)),S&&this.type==="card"?h(Jt,{clsPrefix:o,class:`${o}-tabs-tab__close`,onClick:this.handleClose,disabled:p}):null))}}),Ya=i("tabs",`
 box-sizing: border-box;
 width: 100%;
 display: flex;
 flex-direction: column;
 transition:
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
`,[v("segment-type",[i("tabs-rail",[E("&.transition-disabled",[i("tabs-capsule",`
 transition: none;
 `)])])]),v("top",[i("tab-pane",`
 padding: var(--n-pane-padding-top) var(--n-pane-padding-right) var(--n-pane-padding-bottom) var(--n-pane-padding-left);
 `)]),v("left",[i("tab-pane",`
 padding: var(--n-pane-padding-right) var(--n-pane-padding-bottom) var(--n-pane-padding-left) var(--n-pane-padding-top);
 `)]),v("left, right",`
 flex-direction: row;
 `,[i("tabs-bar",`
 width: 2px;
 right: 0;
 transition:
 top .2s var(--n-bezier),
 max-height .2s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `),i("tabs-tab",`
 padding: var(--n-tab-padding-vertical); 
 `)]),v("right",`
 flex-direction: row-reverse;
 `,[i("tab-pane",`
 padding: var(--n-pane-padding-left) var(--n-pane-padding-top) var(--n-pane-padding-right) var(--n-pane-padding-bottom);
 `),i("tabs-bar",`
 left: 0;
 `)]),v("bottom",`
 flex-direction: column-reverse;
 justify-content: flex-end;
 `,[i("tab-pane",`
 padding: var(--n-pane-padding-bottom) var(--n-pane-padding-right) var(--n-pane-padding-top) var(--n-pane-padding-left);
 `),i("tabs-bar",`
 top: 0;
 `)]),i("tabs-rail",`
 position: relative;
 padding: 3px;
 border-radius: var(--n-tab-border-radius);
 width: 100%;
 background-color: var(--n-color-segment);
 transition: background-color .3s var(--n-bezier);
 display: flex;
 align-items: center;
 `,[i("tabs-capsule",`
 border-radius: var(--n-tab-border-radius);
 position: absolute;
 pointer-events: none;
 background-color: var(--n-tab-color-segment);
 box-shadow: 0 1px 3px 0 rgba(0, 0, 0, .08);
 transition: transform 0.3s var(--n-bezier);
 `),i("tabs-tab-wrapper",`
 flex-basis: 0;
 flex-grow: 1;
 display: flex;
 align-items: center;
 justify-content: center;
 `,[i("tabs-tab",`
 overflow: hidden;
 border-radius: var(--n-tab-border-radius);
 width: 100%;
 display: flex;
 align-items: center;
 justify-content: center;
 `,[v("active",`
 font-weight: var(--n-font-weight-strong);
 color: var(--n-tab-text-color-active);
 `),E("&:hover",`
 color: var(--n-tab-text-color-hover);
 `)])])]),v("flex",[i("tabs-nav",`
 width: 100%;
 position: relative;
 `,[i("tabs-wrapper",`
 width: 100%;
 `,[i("tabs-tab",`
 margin-right: 0;
 `)])])]),i("tabs-nav",`
 box-sizing: border-box;
 line-height: 1.5;
 display: flex;
 transition: border-color .3s var(--n-bezier);
 `,[F("prefix, suffix",`
 display: flex;
 align-items: center;
 `),F("prefix","padding-right: 16px;"),F("suffix","padding-left: 16px;")]),v("top, bottom",[E(">",[i("tabs-nav",[i("tabs-nav-scroll-wrapper",[E("&::before",`
 top: 0;
 bottom: 0;
 left: 0;
 width: 20px;
 `),E("&::after",`
 top: 0;
 bottom: 0;
 right: 0;
 width: 20px;
 `),v("shadow-start",[E("&::before",`
 box-shadow: inset 10px 0 8px -8px rgba(0, 0, 0, .12);
 `)]),v("shadow-end",[E("&::after",`
 box-shadow: inset -10px 0 8px -8px rgba(0, 0, 0, .12);
 `)])])])])]),v("left, right",[i("tabs-nav-scroll-content",`
 flex-direction: column;
 `),E(">",[i("tabs-nav",[i("tabs-nav-scroll-wrapper",[E("&::before",`
 top: 0;
 left: 0;
 right: 0;
 height: 20px;
 `),E("&::after",`
 bottom: 0;
 left: 0;
 right: 0;
 height: 20px;
 `),v("shadow-start",[E("&::before",`
 box-shadow: inset 0 10px 8px -8px rgba(0, 0, 0, .12);
 `)]),v("shadow-end",[E("&::after",`
 box-shadow: inset 0 -10px 8px -8px rgba(0, 0, 0, .12);
 `)])])])])]),i("tabs-nav-scroll-wrapper",`
 flex: 1;
 position: relative;
 overflow: hidden;
 `,[i("tabs-nav-y-scroll",`
 height: 100%;
 width: 100%;
 overflow-y: auto; 
 scrollbar-width: none;
 `,[E("&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb",`
 width: 0;
 height: 0;
 display: none;
 `)]),E("&::before, &::after",`
 transition: box-shadow .3s var(--n-bezier);
 pointer-events: none;
 content: "";
 position: absolute;
 z-index: 1;
 `)]),i("tabs-nav-scroll-content",`
 display: flex;
 position: relative;
 min-width: 100%;
 min-height: 100%;
 width: fit-content;
 box-sizing: border-box;
 `),i("tabs-wrapper",`
 display: inline-flex;
 flex-wrap: nowrap;
 position: relative;
 `),i("tabs-tab-wrapper",`
 display: flex;
 flex-wrap: nowrap;
 flex-shrink: 0;
 flex-grow: 0;
 `),i("tabs-tab",`
 cursor: pointer;
 white-space: nowrap;
 flex-wrap: nowrap;
 display: inline-flex;
 align-items: center;
 color: var(--n-tab-text-color);
 font-size: var(--n-tab-font-size);
 background-clip: padding-box;
 padding: var(--n-tab-padding);
 transition:
 box-shadow .3s var(--n-bezier),
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `,[v("disabled",{cursor:"not-allowed"}),F("close",`
 margin-left: 6px;
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `),F("label",`
 display: flex;
 align-items: center;
 z-index: 1;
 `)]),i("tabs-bar",`
 position: absolute;
 bottom: 0;
 height: 2px;
 border-radius: 1px;
 background-color: var(--n-bar-color);
 transition:
 left .2s var(--n-bezier),
 max-width .2s var(--n-bezier),
 opacity .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `,[E("&.transition-disabled",`
 transition: none;
 `),v("disabled",`
 background-color: var(--n-tab-text-color-disabled)
 `)]),i("tabs-pane-wrapper",`
 position: relative;
 overflow: hidden;
 transition: max-height .2s var(--n-bezier);
 `),i("tab-pane",`
 color: var(--n-pane-text-color);
 width: 100%;
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 opacity .2s var(--n-bezier);
 left: 0;
 right: 0;
 top: 0;
 `,[E("&.next-transition-leave-active, &.prev-transition-leave-active, &.next-transition-enter-active, &.prev-transition-enter-active",`
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 transform .2s var(--n-bezier),
 opacity .2s var(--n-bezier);
 `),E("&.next-transition-leave-active, &.prev-transition-leave-active",`
 position: absolute;
 `),E("&.next-transition-enter-from, &.prev-transition-leave-to",`
 transform: translateX(32px);
 opacity: 0;
 `),E("&.next-transition-leave-to, &.prev-transition-enter-from",`
 transform: translateX(-32px);
 opacity: 0;
 `),E("&.next-transition-leave-from, &.next-transition-enter-to, &.prev-transition-leave-from, &.prev-transition-enter-to",`
 transform: translateX(0);
 opacity: 1;
 `)]),i("tabs-tab-pad",`
 box-sizing: border-box;
 width: var(--n-tab-gap);
 flex-grow: 0;
 flex-shrink: 0;
 `),v("line-type, bar-type",[i("tabs-tab",`
 font-weight: var(--n-tab-font-weight);
 box-sizing: border-box;
 vertical-align: bottom;
 `,[E("&:hover",{color:"var(--n-tab-text-color-hover)"}),v("active",`
 color: var(--n-tab-text-color-active);
 font-weight: var(--n-tab-font-weight-active);
 `),v("disabled",{color:"var(--n-tab-text-color-disabled)"})])]),i("tabs-nav",[v("line-type",[v("top",[F("prefix, suffix",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),i("tabs-nav-scroll-content",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),i("tabs-bar",`
 bottom: -1px;
 `)]),v("left",[F("prefix, suffix",`
 border-right: 1px solid var(--n-tab-border-color);
 `),i("tabs-nav-scroll-content",`
 border-right: 1px solid var(--n-tab-border-color);
 `),i("tabs-bar",`
 right: -1px;
 `)]),v("right",[F("prefix, suffix",`
 border-left: 1px solid var(--n-tab-border-color);
 `),i("tabs-nav-scroll-content",`
 border-left: 1px solid var(--n-tab-border-color);
 `),i("tabs-bar",`
 left: -1px;
 `)]),v("bottom",[F("prefix, suffix",`
 border-top: 1px solid var(--n-tab-border-color);
 `),i("tabs-nav-scroll-content",`
 border-top: 1px solid var(--n-tab-border-color);
 `),i("tabs-bar",`
 top: -1px;
 `)]),F("prefix, suffix",`
 transition: border-color .3s var(--n-bezier);
 `),i("tabs-nav-scroll-content",`
 transition: border-color .3s var(--n-bezier);
 `),i("tabs-bar",`
 border-radius: 0;
 `)]),v("card-type",[F("prefix, suffix",`
 transition: border-color .3s var(--n-bezier);
 `),i("tabs-pad",`
 flex-grow: 1;
 transition: border-color .3s var(--n-bezier);
 `),i("tabs-tab-pad",`
 transition: border-color .3s var(--n-bezier);
 `),i("tabs-tab",`
 font-weight: var(--n-tab-font-weight);
 border: 1px solid var(--n-tab-border-color);
 background-color: var(--n-tab-color);
 box-sizing: border-box;
 position: relative;
 vertical-align: bottom;
 display: flex;
 justify-content: space-between;
 font-size: var(--n-tab-font-size);
 color: var(--n-tab-text-color);
 `,[v("addable",`
 padding-left: 8px;
 padding-right: 8px;
 font-size: 16px;
 justify-content: center;
 `,[F("height-placeholder",`
 width: 0;
 font-size: var(--n-tab-font-size);
 `),ea("disabled",[E("&:hover",`
 color: var(--n-tab-text-color-hover);
 `)])]),v("closable","padding-right: 8px;"),v("active",`
 background-color: #0000;
 font-weight: var(--n-tab-font-weight-active);
 color: var(--n-tab-text-color-active);
 `),v("disabled","color: var(--n-tab-text-color-disabled);")])]),v("left, right",`
 flex-direction: column; 
 `,[F("prefix, suffix",`
 padding: var(--n-tab-padding-vertical);
 `),i("tabs-wrapper",`
 flex-direction: column;
 `),i("tabs-tab-wrapper",`
 flex-direction: column;
 `,[i("tabs-tab-pad",`
 height: var(--n-tab-gap-vertical);
 width: 100%;
 `)])]),v("top",[v("card-type",[i("tabs-scroll-padding","border-bottom: 1px solid var(--n-tab-border-color);"),F("prefix, suffix",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),i("tabs-tab",`
 border-top-left-radius: var(--n-tab-border-radius);
 border-top-right-radius: var(--n-tab-border-radius);
 `,[v("active",`
 border-bottom: 1px solid #0000;
 `)]),i("tabs-tab-pad",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),i("tabs-pad",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `)])]),v("left",[v("card-type",[i("tabs-scroll-padding","border-right: 1px solid var(--n-tab-border-color);"),F("prefix, suffix",`
 border-right: 1px solid var(--n-tab-border-color);
 `),i("tabs-tab",`
 border-top-left-radius: var(--n-tab-border-radius);
 border-bottom-left-radius: var(--n-tab-border-radius);
 `,[v("active",`
 border-right: 1px solid #0000;
 `)]),i("tabs-tab-pad",`
 border-right: 1px solid var(--n-tab-border-color);
 `),i("tabs-pad",`
 border-right: 1px solid var(--n-tab-border-color);
 `)])]),v("right",[v("card-type",[i("tabs-scroll-padding","border-left: 1px solid var(--n-tab-border-color);"),F("prefix, suffix",`
 border-left: 1px solid var(--n-tab-border-color);
 `),i("tabs-tab",`
 border-top-right-radius: var(--n-tab-border-radius);
 border-bottom-right-radius: var(--n-tab-border-radius);
 `,[v("active",`
 border-left: 1px solid #0000;
 `)]),i("tabs-tab-pad",`
 border-left: 1px solid var(--n-tab-border-color);
 `),i("tabs-pad",`
 border-left: 1px solid var(--n-tab-border-color);
 `)])]),v("bottom",[v("card-type",[i("tabs-scroll-padding","border-top: 1px solid var(--n-tab-border-color);"),F("prefix, suffix",`
 border-top: 1px solid var(--n-tab-border-color);
 `),i("tabs-tab",`
 border-bottom-left-radius: var(--n-tab-border-radius);
 border-bottom-right-radius: var(--n-tab-border-radius);
 `,[v("active",`
 border-top: 1px solid #0000;
 `)]),i("tabs-tab-pad",`
 border-top: 1px solid var(--n-tab-border-color);
 `),i("tabs-pad",`
 border-top: 1px solid var(--n-tab-border-color);
 `)])])])]),Ve=Ga,Ka=Object.assign(Object.assign({},dt.props),{value:[String,Number],defaultValue:[String,Number],trigger:{type:String,default:"click"},type:{type:String,default:"bar"},closable:Boolean,justifyContent:String,size:String,placement:{type:String,default:"top"},tabStyle:[String,Object],tabClass:String,addTabStyle:[String,Object],addTabClass:String,barWidth:Number,paneClass:String,paneStyle:[String,Object],paneWrapperClass:String,paneWrapperStyle:[String,Object],addable:[Boolean,Object],tabsPadding:{type:Number,default:0},animated:Boolean,onBeforeLeave:Function,onAdd:Function,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],onClose:[Function,Array],labelSize:String,activeName:[String,Number],onActiveNameChange:[Function,Array]}),Ja=pe({name:"Tabs",props:Ka,slots:Object,setup(e,{slots:o}){var f,p,b,P;const{mergedClsPrefixRef:u,inlineThemeDisabled:S,mergedComponentPropsRef:T}=ta(e),R=dt("Tabs","-tabs",Ya,Xa,e,u),$=w(null),B=w(null),W=w(null),z=w(null),L=w(null),A=w(null),I=w(!0),y=w(!0),_=qe(e,["labelSize","size"]),O=de(()=>{var a,r;if(_.value)return _.value;const d=(r=(a=T==null?void 0:T.value)===null||a===void 0?void 0:a.Tabs)===null||r===void 0?void 0:r.size;return d||"medium"}),M=qe(e,["activeName","value"]),C=w((p=(f=M.value)!==null&&f!==void 0?f:e.defaultValue)!==null&&p!==void 0?p:o.default?(P=(b=We(o.default())[0])===null||b===void 0?void 0:b.props)===null||P===void 0?void 0:P.name:null),g=aa(M,C),V={id:0},G=de(()=>{if(!(!e.justifyContent||e.type==="card"))return{display:"flex",justifyContent:e.justifyContent}});Se(g,()=>{V.id=0,ae(),re()});function H(){var a;const{value:r}=g;return r===null?null:(a=$.value)===null||a===void 0?void 0:a.querySelector(`[data-name="${r}"]`)}function Te(a){if(e.type==="card")return;const{value:r}=B;if(!r)return;const d=r.style.opacity==="0";if(a){const x=`${u.value}-tabs-bar--disabled`,{barWidth:N,placement:U}=e;if(a.dataset.disabled==="true"?r.classList.add(x):r.classList.remove(x),["top","bottom"].includes(U)){if(ve(["top","maxHeight","height"]),typeof N=="number"&&a.offsetWidth>=N){const q=Math.floor((a.offsetWidth-N)/2)+a.offsetLeft;r.style.left=`${q}px`,r.style.maxWidth=`${N}px`}else r.style.left=`${a.offsetLeft}px`,r.style.maxWidth=`${a.offsetWidth}px`;r.style.width="8192px",d&&(r.style.transition="none"),r.offsetWidth,d&&(r.style.transition="",r.style.opacity="1")}else{if(ve(["left","maxWidth","width"]),typeof N=="number"&&a.offsetHeight>=N){const q=Math.floor((a.offsetHeight-N)/2)+a.offsetTop;r.style.top=`${q}px`,r.style.maxHeight=`${N}px`}else r.style.top=`${a.offsetTop}px`,r.style.maxHeight=`${a.offsetHeight}px`;r.style.height="8192px",d&&(r.style.transition="none"),r.offsetHeight,d&&(r.style.transition="",r.style.opacity="1")}}}function ze(){if(e.type==="card")return;const{value:a}=B;a&&(a.style.opacity="0")}function ve(a){const{value:r}=B;if(r)for(const d of a)r.style[d]=""}function ae(){if(e.type==="card")return;const a=H();a?Te(a):ze()}function re(){var a;const r=(a=L.value)===null||a===void 0?void 0:a.$el;if(!r)return;const d=H();if(!d)return;const{scrollLeft:x,offsetWidth:N}=r,{offsetLeft:U,offsetWidth:q}=d;x>U?r.scrollTo({top:0,left:U,behavior:"smooth"}):U+q>x+N&&r.scrollTo({top:0,left:U+q-N,behavior:"smooth"})}const ne=w(null);let ue=0,Q=null;function Re(a){const r=ne.value;if(r){ue=a.getBoundingClientRect().height;const d=`${ue}px`,x=()=>{r.style.height=d,r.style.maxHeight=d};Q?(x(),Q(),Q=null):Q=x}}function Pe(a){const r=ne.value;if(r){const d=a.getBoundingClientRect().height,x=()=>{document.body.offsetHeight,r.style.maxHeight=`${d}px`,r.style.height=`${Math.max(ue,d)}px`};Q?(Q(),Q=null,x()):Q=x}}function $e(){const a=ne.value;if(a){a.style.maxHeight="",a.style.height="";const{paneWrapperStyle:r}=e;if(typeof r=="string")a.style.cssText=r;else if(r){const{maxHeight:d,height:x}=r;d!==void 0&&(a.style.maxHeight=d),x!==void 0&&(a.style.height=x)}}}const ge={value:[]},me=w("next");function Le(a){const r=g.value;let d="next";for(const x of ge.value){if(x===r)break;if(x===a){d="prev";break}}me.value=d,n(a)}function n(a){const{onActiveNameChange:r,onUpdateValue:d,"onUpdate:value":x}=e;r&&ye(r,a),d&&ye(d,a),x&&ye(x,a),C.value=a}function t(a){const{onClose:r}=e;r&&ye(r,a)}function l(){const{value:a}=B;if(!a)return;const r="transition-disabled";a.classList.add(r),ae(),a.classList.remove(r)}const k=w(null);function j({transitionDisabled:a}){const r=$.value;if(!r)return;a&&r.classList.add("transition-disabled");const d=H();d&&k.value&&(k.value.style.width=`${d.offsetWidth}px`,k.value.style.height=`${d.offsetHeight}px`,k.value.style.transform=`translateX(${d.offsetLeft-oa(getComputedStyle(r).paddingLeft)}px)`,a&&k.value.offsetWidth),a&&r.classList.remove("transition-disabled")}Se([g],()=>{e.type==="segment"&&Ee(()=>{j({transitionDisabled:!1})})}),ut(()=>{e.type==="segment"&&j({transitionDisabled:!0})});let te=0;function ke(a){var r;if(a.contentRect.width===0&&a.contentRect.height===0||te===a.contentRect.width)return;te=a.contentRect.width;const{type:d}=e;if((d==="line"||d==="bar")&&l(),d!=="segment"){const{placement:x}=e;Be((x==="top"||x==="bottom"?(r=L.value)===null||r===void 0?void 0:r.$el:A.value)||null)}}const bt=Ve(ke,64);Se([()=>e.justifyContent,()=>e.size],()=>{Ee(()=>{const{type:a}=e;(a==="line"||a==="bar")&&l()})});const le=w(!1);function ft(a){var r;const{target:d,contentRect:{width:x,height:N}}=a,U=d.parentElement.parentElement.offsetWidth,q=d.parentElement.parentElement.offsetHeight,{placement:ie}=e;if(!le.value)ie==="top"||ie==="bottom"?U<x&&(le.value=!0):q<N&&(le.value=!0);else{const{value:ce}=z;if(!ce)return;ie==="top"||ie==="bottom"?U-x>ce.$el.offsetWidth&&(le.value=!1):q-N>ce.$el.offsetHeight&&(le.value=!1)}Be(((r=L.value)===null||r===void 0?void 0:r.$el)||null)}const pt=Ve(ft,64);function vt(){const{onAdd:a}=e;a&&a(),Ee(()=>{const r=H(),{value:d}=L;!r||!d||d.scrollTo({left:r.offsetLeft,top:0,behavior:"smooth"})})}function Be(a){if(!a)return;const{placement:r}=e;if(r==="top"||r==="bottom"){const{scrollLeft:d,scrollWidth:x,offsetWidth:N}=a;I.value=d<=0,y.value=d+N>=x}else{const{scrollTop:d,scrollHeight:x,offsetHeight:N}=a;I.value=d<=0,y.value=d+N>=x}}const gt=Ve(a=>{Be(a.target)},64);ca(He,{triggerRef:K(e,"trigger"),tabStyleRef:K(e,"tabStyle"),tabClassRef:K(e,"tabClass"),addTabStyleRef:K(e,"addTabStyle"),addTabClassRef:K(e,"addTabClass"),paneClassRef:K(e,"paneClass"),paneStyleRef:K(e,"paneStyle"),mergedClsPrefixRef:u,typeRef:K(e,"type"),closableRef:K(e,"closable"),valueRef:g,tabChangeIdRef:V,onBeforeLeaveRef:K(e,"onBeforeLeave"),activateTab:Le,handleClose:t,handleAdd:vt}),ra(()=>{ae(),re()}),na(()=>{const{value:a}=W;if(!a)return;const{value:r}=u,d=`${r}-tabs-nav-scroll-wrapper--shadow-start`,x=`${r}-tabs-nav-scroll-wrapper--shadow-end`;I.value?a.classList.remove(d):a.classList.add(d),y.value?a.classList.remove(x):a.classList.add(x)});const mt={syncBarPosition:()=>{ae()}},ht=()=>{j({transitionDisabled:!0})},De=de(()=>{const{value:a}=O,{type:r}=e,d={card:"Card",bar:"Bar",line:"Line",segment:"Segment"}[r],x=`${a}${d}`,{self:{barColor:N,closeIconColor:U,closeIconColorHover:q,closeIconColorPressed:ie,tabColor:ce,tabBorderColor:xt,paneTextColor:yt,tabFontWeight:_t,tabBorderRadius:Ct,tabFontWeightActive:St,colorSegment:wt,fontWeightStrong:Tt,tabColorSegment:zt,closeSize:Rt,closeIconSize:Pt,closeColorHover:$t,closeColorPressed:Lt,closeBorderRadius:kt,[Y("panePadding",a)]:he,[Y("tabPadding",x)]:Bt,[Y("tabPaddingVertical",x)]:Wt,[Y("tabGap",x)]:At,[Y("tabGap",`${x}Vertical`)]:Et,[Y("tabTextColor",r)]:It,[Y("tabTextColorActive",r)]:Nt,[Y("tabTextColorHover",r)]:jt,[Y("tabTextColorDisabled",r)]:Mt,[Y("tabFontSize",a)]:Vt},common:{cubicBezierEaseInOut:Ft}}=R.value;return{"--n-bezier":Ft,"--n-color-segment":wt,"--n-bar-color":N,"--n-tab-font-size":Vt,"--n-tab-text-color":It,"--n-tab-text-color-active":Nt,"--n-tab-text-color-disabled":Mt,"--n-tab-text-color-hover":jt,"--n-pane-text-color":yt,"--n-tab-border-color":xt,"--n-tab-border-radius":Ct,"--n-close-size":Rt,"--n-close-icon-size":Pt,"--n-close-color-hover":$t,"--n-close-color-pressed":Lt,"--n-close-border-radius":kt,"--n-close-icon-color":U,"--n-close-icon-color-hover":q,"--n-close-icon-color-pressed":ie,"--n-tab-color":ce,"--n-tab-font-weight":_t,"--n-tab-font-weight-active":St,"--n-tab-padding":Bt,"--n-tab-padding-vertical":Wt,"--n-tab-gap":At,"--n-tab-gap-vertical":Et,"--n-pane-padding-left":xe(he,"left"),"--n-pane-padding-right":xe(he,"right"),"--n-pane-padding-top":xe(he,"top"),"--n-pane-padding-bottom":xe(he,"bottom"),"--n-font-weight-strong":Tt,"--n-tab-color-segment":zt}}),oe=S?la("tabs",de(()=>`${O.value[0]}${e.type[0]}`),De,e):void 0;return Object.assign({mergedClsPrefix:u,mergedValue:g,renderedNames:new Set,segmentCapsuleElRef:k,tabsPaneWrapperRef:ne,tabsElRef:$,barElRef:B,addTabInstRef:z,xScrollInstRef:L,scrollWrapperElRef:W,addTabFixed:le,tabWrapperStyle:G,handleNavResize:bt,mergedSize:O,handleScroll:gt,handleTabsResize:pt,cssVars:S?void 0:De,themeClass:oe==null?void 0:oe.themeClass,animationDirection:me,renderNameListRef:ge,yScrollElRef:A,handleSegmentResize:ht,onAnimationBeforeLeave:Re,onAnimationEnter:Pe,onAnimationAfterEnter:$e,onRender:oe==null?void 0:oe.onRender},mt)},render(){const{mergedClsPrefix:e,type:o,placement:f,addTabFixed:p,addable:b,mergedSize:P,renderNameListRef:u,onRender:S,paneWrapperClass:T,paneWrapperStyle:R,$slots:{default:$,prefix:B,suffix:W}}=this;S==null||S();const z=$?We($()).filter(C=>C.type.__TAB_PANE__===!0):[],L=$?We($()).filter(C=>C.type.__TAB__===!0):[],A=!L.length,I=o==="card",y=o==="segment",_=!I&&!y&&this.justifyContent;u.value=[];const O=()=>{const C=h("div",{style:this.tabWrapperStyle,class:`${e}-tabs-wrapper`},_?null:h("div",{class:`${e}-tabs-scroll-padding`,style:f==="top"||f==="bottom"?{width:`${this.tabsPadding}px`}:{height:`${this.tabsPadding}px`}}),A?z.map((g,V)=>(u.value.push(g.props.name),Fe(h(Oe,Object.assign({},g.props,{internalCreatedByPane:!0,internalLeftPadded:V!==0&&(!_||_==="center"||_==="start"||_==="end")}),g.children?{default:g.children.tab}:void 0)))):L.map((g,V)=>(u.value.push(g.props.name),Fe(V!==0&&!_?ot(g):g))),!p&&b&&I?lt(b,(A?z.length:L.length)!==0):null,_?null:h("div",{class:`${e}-tabs-scroll-padding`,style:{width:`${this.tabsPadding}px`}}));return h("div",{ref:"tabsElRef",class:`${e}-tabs-nav-scroll-content`},I&&b?h(Ae,{onResize:this.handleTabsResize},{default:()=>C}):C,I?h("div",{class:`${e}-tabs-pad`}):null,I?null:h("div",{ref:"barElRef",class:`${e}-tabs-bar`}))},M=y?"top":f;return h("div",{class:[`${e}-tabs`,this.themeClass,`${e}-tabs--${o}-type`,`${e}-tabs--${P}-size`,_&&`${e}-tabs--flex`,`${e}-tabs--${M}`],style:this.cssVars},h("div",{class:[`${e}-tabs-nav--${o}-type`,`${e}-tabs-nav--${M}`,`${e}-tabs-nav`]},Ue(B,C=>C&&h("div",{class:`${e}-tabs-nav__prefix`},C)),y?h(Ae,{onResize:this.handleSegmentResize},{default:()=>h("div",{class:`${e}-tabs-rail`,ref:"tabsElRef"},h("div",{class:`${e}-tabs-capsule`,ref:"segmentCapsuleElRef"},h("div",{class:`${e}-tabs-wrapper`},h("div",{class:`${e}-tabs-tab`}))),A?z.map((C,g)=>(u.value.push(C.props.name),h(Oe,Object.assign({},C.props,{internalCreatedByPane:!0,internalLeftPadded:g!==0}),C.children?{default:C.children.tab}:void 0))):L.map((C,g)=>(u.value.push(C.props.name),g===0?C:ot(C))))}):h(Ae,{onResize:this.handleNavResize},{default:()=>h("div",{class:`${e}-tabs-nav-scroll-wrapper`,ref:"scrollWrapperElRef"},["top","bottom"].includes(M)?h(ka,{ref:"xScrollInstRef",onScroll:this.handleScroll},{default:O}):h("div",{class:`${e}-tabs-nav-y-scroll`,onScroll:this.handleScroll,ref:"yScrollElRef"},O()))}),p&&b&&I?lt(b,!0):null,Ue(W,C=>C&&h("div",{class:`${e}-tabs-nav__suffix`},C))),A&&(this.animated&&(M==="top"||M==="bottom")?h("div",{ref:"tabsPaneWrapperRef",style:R,class:[`${e}-tabs-pane-wrapper`,T]},nt(z,this.mergedValue,this.renderedNames,this.onAnimationBeforeLeave,this.onAnimationEnter,this.onAnimationAfterEnter,this.animationDirection)):nt(z,this.mergedValue,this.renderedNames)))}});function nt(e,o,f,p,b,P,u){const S=[];return e.forEach(T=>{const{name:R,displayDirective:$,"display-directive":B}=T.props,W=L=>$===L||B===L,z=o===R;if(T.key!==void 0&&(T.key=R),z||W("show")||W("show:lazy")&&f.has(R)){f.has(R)||f.add(R);const L=!W("if");S.push(L?ia(T,[[sa,z]]):T)}}),u?h(da,{name:`${u}-transition`,onBeforeLeave:p,onEnter:b,onAfterEnter:P},{default:()=>S}):S}function lt(e,o){return h(Oe,{ref:"addTabInstRef",key:"__addable",name:"__addable",internalCreatedByPane:!0,internalAddable:!0,internalLeftPadded:o,disabled:typeof e=="object"&&e.disabled})}function ot(e){const o=ua(e);return o.props?o.props.internalLeftPadded=!0:o.props={internalLeftPadded:!0},o}function Fe(e){return Array.isArray(e.dynamicProps)?e.dynamicProps.includes("internalLeftPadded")||e.dynamicProps.push("internalLeftPadded"):e.dynamicProps=["internalLeftPadded"],e}const ee={list:()=>Z.get("/suites"),get:e=>Z.get(`/suites/${e}`),create:e=>Z.post("/suites",e),update:(e,o)=>Z.put(`/suites/${e}`,o),delete:e=>Z.delete(`/suites/${e}`),run:(e,o)=>Z.post(`/suites/${e}/runs`,o),listRuns:e=>Z.get(`/suites/${e}/runs`),getRun:(e,o)=>Z.get(`/suites/${e}/runs/${o}`)},Za={style:{color:"#999","font-size":"13px"}},er={style:{"font-weight":"600","margin-bottom":"8px"}},tr={style:{color:"#999","font-size":"13px","font-weight":"normal"}},_r=pe({__name:"SuiteCenter",setup(e){const o=ba(),f=ma(),p=Ta(),b=w([]),P=w(!1),u=w(null),S=w([]),T=w(!1),R=w(!1),$=w(!1),B=w(!1),W=w(null),z=w(null),L=w([]),A=w([]),I=w({}),y=w({target_app_id:"",environment:"",override_host:"",concurrency:void 0,perf_threshold_ms:void 0}),_=w({name:"",description:"",default_target_app_id:void 0,default_environment:"",default_concurrency:1,default_delay_ms:0,default_perf_threshold_ms:void 0}),O=w(Ke(o.query,"keyword")||""),M=w(Ke(o.query,"app_id")),C=w(Ca(o.query,"created_from","created_to")),g=ya(),V=de(()=>{let n=b.value;if(O.value){const t=O.value.toLowerCase();n=n.filter(l=>l.name.toLowerCase().includes(t))}return M.value&&(n=n.filter(t=>t.default_target_app_id===M.value)),C.value&&(n=n.filter(t=>_a(t.created_at,C.value))),n}),G=Qe({page:1,pageSize:10,showSizePicker:!0,pageSizes:[10,20,50],onChange:n=>{G.page=n},onUpdatePageSize:n=>{G.pageSize=n,G.page=1}}),H=Qe({page:1,pageSize:10,showSizePicker:!0,pageSizes:[10,20,50],onChange:n=>{H.page=n},onUpdatePageSize:n=>{H.pageSize=n,H.page=1}}),Te=n=>n>=.9?"#18a058":n>=.6?"#f0a020":"#d03050",ze=[{title:"名称",key:"name"},{title:"用例数",key:"case_count",render:n=>{var t;return((t=n.case_ids)==null?void 0:t.length)??0}},{title:"默认环境",key:"default_environment",render:n=>n.default_environment||"-"},{title:"创建时间",key:"created_at",render:n=>Ye(n.created_at)},{title:"操作",key:"actions",width:120,render:n=>h(J,{size:"small",onClick:()=>ne(n)},()=>"查看/执行")}],ve=[{title:"状态",key:"status",width:90,render:n=>h("span",{style:`color:${n.status==="DONE"?"#18a058":n.status==="FAILED"?"#d03050":"#f0a020"}`},n.status==="DONE"?"已完成":n.status==="FAILED"?"失败":"运行中")},{title:"用例",key:"cases",render:n=>`${n.passed_cases}/${n.total_cases} 通过`},{title:"通过率",key:"rate",render:n=>{const t=Math.round((n.overall_pass_rate??0)*100);return h("span",{style:`color:${Te(n.overall_pass_rate??0)};font-weight:bold`},`${t}%`)}},{title:"开始时间",key:"started_at",render:n=>Ye(n.started_at)},{title:"操作",key:"actions",width:120,render:n=>{var t;return(t=n.job_ids)!=null&&t.length?h(J,{size:"small",onClick:()=>f.push(`/results/${n.job_ids[0]}`)},()=>"查看第1个任务"):"-"}}];async function ae(){P.value=!0;try{const n=await ee.list();b.value=n.data}finally{P.value=!1}}async function re(n){T.value=!0;try{const t=await ee.listRuns(n);S.value=t.data}finally{T.value=!1}}function ne(n){u.value=n,H.page=1,y.value={target_app_id:n.default_target_app_id||"",environment:n.default_environment||"",override_host:n.default_override_host||"",concurrency:void 0,perf_threshold_ms:n.default_perf_threshold_ms??void 0},re(n.id)}function ue(){W.value=null,_.value={name:"",description:"",default_target_app_id:void 0,default_environment:"",default_concurrency:1,default_delay_ms:0,default_perf_threshold_ms:void 0},B.value=!0}function Q(){O.value="",M.value=null,C.value=null}function Re(n){W.value=n.id,_.value={name:n.name,description:n.description||"",default_target_app_id:n.default_target_app_id||void 0,default_environment:n.default_environment||"",default_concurrency:n.default_concurrency??1,default_delay_ms:n.default_delay_ms??0,default_perf_threshold_ms:n.default_perf_threshold_ms??void 0},B.value=!0}async function Pe(){var n,t,l;if(!_.value.name){p.warning("请填写套件名称");return}$.value=!0;try{const k={..._.value};if(k.default_environment||delete k.default_environment,k.description||delete k.description,k.default_perf_threshold_ms||delete k.default_perf_threshold_ms,W.value){const j=await ee.update(W.value,k),te=b.value.findIndex(ke=>ke.id===W.value);te>=0&&(b.value[te]=j.data),((n=u.value)==null?void 0:n.id)===W.value&&(u.value=j.data)}else{const j=await ee.create(k);b.value.unshift(j.data)}B.value=!1,p.success("保存成功")}catch(k){p.error(((l=(t=k.response)==null?void 0:t.data)==null?void 0:l.detail)||"保存失败")}finally{$.value=!1}}async function $e(n){var t,l,k;try{await ee.delete(n),b.value=b.value.filter(j=>j.id!==n),((t=u.value)==null?void 0:t.id)===n&&(u.value=null),p.success("已删除")}catch(j){p.error(((k=(l=j.response)==null?void 0:l.data)==null?void 0:k.detail)||"删除失败")}}async function ge(){var n,t;if(u.value){if(!y.value.target_app_id){p.warning("请选择目标应用");return}R.value=!0;try{const l={target_app_id:y.value.target_app_id};y.value.environment&&(l.environment=y.value.environment),y.value.override_host&&(l.override_host=y.value.override_host),y.value.concurrency&&(l.concurrency=y.value.concurrency),y.value.perf_threshold_ms&&(l.perf_threshold_ms=y.value.perf_threshold_ms),await ee.run(u.value.id,l),p.success("套件已开始执行"),await re(u.value.id)}catch(l){p.error(((t=(n=l.response)==null?void 0:n.data)==null?void 0:t.detail)||"执行失败")}finally{R.value=!1}}}async function me(n){if(!n||!u.value)return;const t=u.value.case_ids||[];if(t.includes(n)){p.warning("用例已在套件中"),z.value=null;return}const l=[...t,n],k=await ee.update(u.value.id,{case_ids:l});u.value=k.data;const j=b.value.findIndex(te=>te.id===u.value.id);j>=0&&(b.value[j]=k.data),z.value=null,p.success("已添加")}async function Le(n){if(!u.value)return;const t=(u.value.case_ids||[]).filter(j=>j!==n),l=await ee.update(u.value.id,{case_ids:t});u.value=l.data;const k=b.value.findIndex(j=>j.id===u.value.id);k>=0&&(b.value[k]=l.data)}return ut(async()=>{const[n,t]=await Promise.all([ha.list(),xa.list({limit:500})]);L.value=n.data.map(l=>({label:l.name,value:l.id})),A.value=t.data.items.map(l=>({label:l.name,value:l.id})),I.value=Object.fromEntries(t.data.items.map(l=>[l.id,l.name])),await ae()}),Se([O,M,C],()=>{const n={};Je(n,"keyword",O.value.trim()||null),Je(n,"app_id",M.value),Sa(n,C.value,"created_from","created_to"),f.replace({query:n})}),(n,t)=>(_e(),Ie(s(be),{vertical:"",size:16},{default:m(()=>[c(s(Xe),{title:"回放套件"},{"header-extra":m(()=>[c(s(be),null,{default:m(()=>[c(s(se),{value:O.value,"onUpdate:value":t[0]||(t[0]=l=>O.value=l),placeholder:"搜索套件名称",clearable:"",style:{width:"180px"}},null,8,["value"]),c(s(Ce),{value:M.value,"onUpdate:value":t[1]||(t[1]=l=>M.value=l),options:L.value,placeholder:"默认目标应用",clearable:"",style:{width:"160px"}},null,8,["value","options"]),c(s(za),{value:C.value,"onUpdate:value":t[2]||(t[2]=l=>C.value=l),type:"datetimerange",clearable:"",shortcuts:s(g),style:{width:"320px"},"start-placeholder":"创建开始时间","end-placeholder":"创建结束时间"},null,8,["value","shortcuts"]),c(s(J),{size:"small",onClick:Q},{default:m(()=>[...t[21]||(t[21]=[X("清空筛选",-1)])]),_:1}),c(s(J),{type:"primary",size:"small",onClick:ue},{default:m(()=>[...t[22]||(t[22]=[X("+ 新建套件",-1)])]),_:1})]),_:1})]),default:m(()=>[c(s(be),{align:"center",style:{"margin-bottom":"10px"}},{default:m(()=>[Ne("span",Za,"共 "+je(V.value.length)+" 条",1)]),_:1}),c(s(Ze),{columns:ze,data:V.value,loading:P.value,"row-key":l=>l.id,pagination:G},null,8,["data","loading","row-key","pagination"])]),_:1}),u.value?(_e(),Ie(s(Xe),{key:0,title:`套件：${u.value.name}`},{"header-extra":m(()=>[c(s(be),null,{default:m(()=>[c(s(J),{size:"small",onClick:t[3]||(t[3]=l=>Re(u.value))},{default:m(()=>[...t[23]||(t[23]=[X("编辑",-1)])]),_:1}),c(s(Pa),{onPositiveClick:t[4]||(t[4]=l=>$e(u.value.id))},{trigger:m(()=>[c(s(J),{size:"small",type:"error"},{default:m(()=>[...t[24]||(t[24]=[X("删除",-1)])]),_:1})]),default:m(()=>[t[25]||(t[25]=X(" 确认删除套件？ ",-1))]),_:1})]),_:1})]),default:m(()=>[c(s(Ja),{type:"line",animated:""},{default:m(()=>[c(s(rt),{name:"run",tab:"执行套件"},{default:m(()=>[c(s(et),{"label-placement":"left","label-width":"130px",style:{"max-width":"560px","margin-top":"12px"}},{default:m(()=>[c(s(D),{label:"回放目标应用",required:""},{default:m(()=>[c(s(Ce),{value:y.value.target_app_id,"onUpdate:value":t[5]||(t[5]=l=>y.value.target_app_id=l),options:L.value,placeholder:"选择目标应用"},null,8,["value","options"])]),_:1}),c(s(D),{label:"环境标签"},{default:m(()=>[c(s(se),{value:y.value.environment,"onUpdate:value":t[6]||(t[6]=l=>y.value.environment=l),placeholder:"staging / test（留空用套件默认）"},null,8,["value"])]),_:1}),c(s(D),{label:"Host 覆盖"},{default:m(()=>[c(s(se),{value:y.value.override_host,"onUpdate:value":t[7]||(t[7]=l=>y.value.override_host=l),placeholder:"留空用套件默认"},null,8,["value"])]),_:1}),c(s(D),{label:"并发数"},{default:m(()=>[c(s(fe),{value:y.value.concurrency,"onUpdate:value":t[8]||(t[8]=l=>y.value.concurrency=l),min:1,max:20,placeholder:"留空用套件默认"},null,8,["value"])]),_:1}),c(s(D),{label:"性能阈值(ms)"},{default:m(()=>[c(s(fe),{value:y.value.perf_threshold_ms,"onUpdate:value":t[9]||(t[9]=l=>y.value.perf_threshold_ms=l),min:0,placeholder:"超过此耗时标记 PERF FAIL"},null,8,["value"])]),_:1}),c(s(D),null,{default:m(()=>[c(s(J),{type:"primary",loading:R.value,onClick:ge},{default:m(()=>[...t[26]||(t[26]=[X("执行套件",-1)])]),_:1},8,["loading"])]),_:1})]),_:1}),c(s(Ra)),Ne("div",er,[t[27]||(t[27]=X("执行历史 ",-1)),Ne("span",tr,"共 "+je(S.value.length)+" 条",1)]),c(s(Ze),{columns:ve,data:S.value,loading:T.value,size:"small",pagination:H},null,8,["data","loading","pagination"]),c(s(J),{size:"tiny",style:{"margin-top":"8px"},onClick:t[10]||(t[10]=l=>re(u.value.id))},{default:m(()=>[...t[28]||(t[28]=[X("刷新",-1)])]),_:1})]),_:1}),c(s(rt),{name:"cases",tab:"包含用例"},{default:m(()=>[c(s(be),{vertical:"",size:8,style:{"margin-top":"12px"}},{default:m(()=>[(_e(!0),fa(st,null,pa(u.value.case_ids,l=>(_e(),Ie(s($a),{key:l,closable:"",onClose:k=>Le(l)},{default:m(()=>[X(je(I.value[l]||l.slice(0,8)),1)]),_:2},1032,["onClose"]))),128)),c(s(Ce),{value:z.value,"onUpdate:value":[t[11]||(t[11]=l=>z.value=l),me],options:A.value,filterable:"",clearable:"",placeholder:"添加测试用例",style:{width:"300px"}},null,8,["value","options"])]),_:1})]),_:1})]),_:1})]),_:1},8,["title"])):va("",!0),c(s(ga),{show:B.value,"onUpdate:show":t[20]||(t[20]=l=>B.value=l),preset:"dialog",title:W.value?"编辑套件":"新建套件",style:{width:"520px"}},{action:m(()=>[c(s(J),{onClick:t[19]||(t[19]=l=>B.value=!1)},{default:m(()=>[...t[29]||(t[29]=[X("取消",-1)])]),_:1}),c(s(J),{type:"primary",loading:$.value,onClick:Pe},{default:m(()=>[...t[30]||(t[30]=[X("保存",-1)])]),_:1},8,["loading"])]),default:m(()=>[c(s(et),{model:_.value,"label-placement":"left","label-width":"130px"},{default:m(()=>[c(s(D),{label:"套件名称",required:""},{default:m(()=>[c(s(se),{value:_.value.name,"onUpdate:value":t[12]||(t[12]=l=>_.value.name=l),placeholder:"如：用户模块回归测试"},null,8,["value"])]),_:1}),c(s(D),{label:"描述"},{default:m(()=>[c(s(se),{value:_.value.description,"onUpdate:value":t[13]||(t[13]=l=>_.value.description=l),type:"textarea",rows:2},null,8,["value"])]),_:1}),c(s(D),{label:"默认目标应用"},{default:m(()=>[c(s(Ce),{value:_.value.default_target_app_id,"onUpdate:value":t[14]||(t[14]=l=>_.value.default_target_app_id=l),options:L.value,clearable:"",placeholder:"运行时可覆盖"},null,8,["value","options"])]),_:1}),c(s(D),{label:"默认环境"},{default:m(()=>[c(s(se),{value:_.value.default_environment,"onUpdate:value":t[15]||(t[15]=l=>_.value.default_environment=l),placeholder:"staging"},null,8,["value"])]),_:1}),c(s(D),{label:"默认并发数"},{default:m(()=>[c(s(fe),{value:_.value.default_concurrency,"onUpdate:value":t[16]||(t[16]=l=>_.value.default_concurrency=l),min:1,max:20},null,8,["value"])]),_:1}),c(s(D),{label:"默认延迟(ms)"},{default:m(()=>[c(s(fe),{value:_.value.default_delay_ms,"onUpdate:value":t[17]||(t[17]=l=>_.value.default_delay_ms=l),min:0},null,8,["value"])]),_:1}),c(s(D),{label:"默认性能阈值(ms)"},{default:m(()=>[c(s(fe),{value:_.value.default_perf_threshold_ms,"onUpdate:value":t[18]||(t[18]=l=>_.value.default_perf_threshold_ms=l),min:0,clearable:"",placeholder:"不限制"},null,8,["value"])]),_:1})]),_:1},8,["model"])]),_:1},8,["show","title"])]),_:1}))}});export{_r as default};
