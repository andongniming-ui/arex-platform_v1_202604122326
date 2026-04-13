import{d as pe,n as m,bi as Vt,r as w,bj as Ft,bk as Ue,bl as Ot,bm as we,bn as Ht,p as Dt,a8 as Gt,al as Ut,ag as ot,aV as Xt,F as it,ab as qt,bo as Yt,b3 as Kt,m as re,bp as Jt,s as i,v as p,q as E,x as F,aa as Zt,bq as We,ba as Xe,br as Ae,I as Qt,J as st,L as ea,w as _e,o as dt,bs as ta,am as aa,M as ra,bc as qe,bh as na,ad as la,af as oa,bt as ia,bu as sa,S as Ee,at as K,bf as ye,ak as da,U as J,P as Ce,a as ua,W as Ne,e as g,u,k as be,g as ca,b,j as Ie,t as je,B as Z,l as Y,N as Ye,c as ba,Z as fa,Y as pa,f as va,aF as Ke,h as ga,i as Se}from"./index-By7nBA3K.js";import{c as ee}from"./client-DofY_RJ9.js";import{a as ma}from"./applications-WwaMyD6G.js";import{t as ha}from"./testCases-CYIfek59.js";import{f as Je}from"./time-DBiNR5Lf.js";import{c as xa,i as ya}from"./dateRange-BwFEbxrI.js";import{A as Ca}from"./Add-BuYEuuYZ.js";import{u as Sa}from"./use-message-Pmc6Kr4V.js";import{N as Ze}from"./DataTable-DJ-khQNJ.js";import{N as de}from"./Input-B2P9R1ZR.js";import{N as _a}from"./DatePicker-yIy_OLrE.js";import{N as Qe}from"./Form-8se9H-vE.js";import{N as H}from"./FormItem-DHbjwu74.js";import{N as Me}from"./Select-DoIi1uD2.js";import{N as fe}from"./InputNumber-BeX4Hreq.js";import{N as wa}from"./Divider-D9YTe3Vt.js";import{N as Ta}from"./Popconfirm-CCNS25QZ.js";import{N as za}from"./Tag-jBJuUJOE.js";const Pa=Ue(".v-x-scroll",{overflow:"auto",scrollbarWidth:"none"},[Ue("&::-webkit-scrollbar",{width:0,height:0})]),Ra=pe({name:"XScroll",props:{disabled:Boolean,onScroll:Function},setup(){const e=w(null);function o(v){!(v.currentTarget.offsetWidth<v.currentTarget.scrollWidth)||v.deltaY===0||(v.currentTarget.scrollLeft+=v.deltaY+v.deltaX,v.preventDefault())}const s=Ft();return Pa.mount({id:"vueuc/x-scroll",head:!0,anchorMetaName:Vt,ssr:s}),Object.assign({selfRef:e,handleWheel:o},{scrollTo(...v){var y;(y=e.value)===null||y===void 0||y.scrollTo(...v)}})},render(){return m("div",{ref:"selfRef",onScroll:this.onScroll,onWheel:this.disabled?void 0:this.handleWheel,class:"v-x-scroll"},this.$slots)}});var $a=/\s/;function La(e){for(var o=e.length;o--&&$a.test(e.charAt(o)););return o}var ka=/^\s+/;function Ba(e){return e&&e.slice(0,La(e)+1).replace(ka,"")}var et=NaN,Wa=/^[-+]0x[0-9a-f]+$/i,Aa=/^0b[01]+$/i,Ea=/^0o[0-7]+$/i,Na=parseInt;function tt(e){if(typeof e=="number")return e;if(Ot(e))return et;if(we(e)){var o=typeof e.valueOf=="function"?e.valueOf():e;e=we(o)?o+"":o}if(typeof e!="string")return e===0?e:+e;e=Ba(e);var s=Aa.test(e);return s||Ea.test(e)?Na(e.slice(2),s?2:8):Wa.test(e)?et:+e}var Ve=function(){return Ht.Date.now()},Ia="Expected a function",ja=Math.max,Ma=Math.min;function Va(e,o,s){var S,v,y,T,d,z,P=0,$=!1,A=!1,B=!0;if(typeof e!="function")throw new TypeError(Ia);o=tt(o)||0,we(s)&&($=!!s.leading,A="maxWait"in s,y=A?ja(tt(s.maxWait)||0,o):y,B="trailing"in s?!!s.trailing:B);function _(f){var M=S,U=v;return S=v=void 0,P=f,T=e.apply(U,M),T}function L(f){return P=f,d=setTimeout(j,o),$?_(f):T}function W(f){var M=f-z,U=f-P,D=o-M;return A?Ma(D,y-U):D}function N(f){var M=f-z,U=f-P;return z===void 0||M>=o||M<0||A&&U>=y}function j(){var f=Ve();if(N(f))return h(f);d=setTimeout(j,W(f))}function h(f){return d=void 0,B&&S?_(f):(S=v=void 0,T)}function R(){d!==void 0&&clearTimeout(d),P=0,S=z=v=d=void 0}function O(){return d===void 0?T:h(Ve())}function C(){var f=Ve(),M=N(f);if(S=arguments,v=this,z=f,M){if(d===void 0)return L(z);if(A)return clearTimeout(d),d=setTimeout(j,o),_(z)}return d===void 0&&(d=setTimeout(j,o)),T}return C.cancel=R,C.flush=O,C}var Fa="Expected a function";function Oa(e,o,s){var S=!0,v=!0;if(typeof e!="function")throw new TypeError(Fa);return we(s)&&(S="leading"in s?!!s.leading:S,v="trailing"in s?!!s.trailing:v),Va(e,o,{leading:S,maxWait:o,trailing:v})}const Ha={tabFontSizeSmall:"14px",tabFontSizeMedium:"14px",tabFontSizeLarge:"16px",tabGapSmallLine:"36px",tabGapMediumLine:"36px",tabGapLargeLine:"36px",tabGapSmallLineVertical:"8px",tabGapMediumLineVertical:"8px",tabGapLargeLineVertical:"8px",tabPaddingSmallLine:"6px 0",tabPaddingMediumLine:"10px 0",tabPaddingLargeLine:"14px 0",tabPaddingVerticalSmallLine:"6px 12px",tabPaddingVerticalMediumLine:"8px 16px",tabPaddingVerticalLargeLine:"10px 20px",tabGapSmallBar:"36px",tabGapMediumBar:"36px",tabGapLargeBar:"36px",tabGapSmallBarVertical:"8px",tabGapMediumBarVertical:"8px",tabGapLargeBarVertical:"8px",tabPaddingSmallBar:"4px 0",tabPaddingMediumBar:"6px 0",tabPaddingLargeBar:"10px 0",tabPaddingVerticalSmallBar:"6px 12px",tabPaddingVerticalMediumBar:"8px 16px",tabPaddingVerticalLargeBar:"10px 20px",tabGapSmallCard:"4px",tabGapMediumCard:"4px",tabGapLargeCard:"4px",tabGapSmallCardVertical:"4px",tabGapMediumCardVertical:"4px",tabGapLargeCardVertical:"4px",tabPaddingSmallCard:"8px 16px",tabPaddingMediumCard:"10px 20px",tabPaddingLargeCard:"12px 24px",tabPaddingSmallSegment:"4px 0",tabPaddingMediumSegment:"6px 0",tabPaddingLargeSegment:"8px 0",tabPaddingVerticalLargeSegment:"0 8px",tabPaddingVerticalSmallCard:"8px 12px",tabPaddingVerticalMediumCard:"10px 16px",tabPaddingVerticalLargeCard:"12px 20px",tabPaddingVerticalSmallSegment:"0 4px",tabPaddingVerticalMediumSegment:"0 6px",tabGapSmallSegment:"0",tabGapMediumSegment:"0",tabGapLargeSegment:"0",tabGapSmallSegmentVertical:"0",tabGapMediumSegmentVertical:"0",tabGapLargeSegmentVertical:"0",panePaddingSmall:"8px 0 0 0",panePaddingMedium:"12px 0 0 0",panePaddingLarge:"16px 0 0 0",closeSize:"18px",closeIconSize:"14px"};function Da(e){const{textColor2:o,primaryColor:s,textColorDisabled:S,closeIconColor:v,closeIconColorHover:y,closeIconColorPressed:T,closeColorHover:d,closeColorPressed:z,tabColor:P,baseColor:$,dividerColor:A,fontWeight:B,textColor1:_,borderRadius:L,fontSize:W,fontWeightStrong:N}=e;return Object.assign(Object.assign({},Ha),{colorSegment:P,tabFontSizeCard:W,tabTextColorLine:_,tabTextColorActiveLine:s,tabTextColorHoverLine:s,tabTextColorDisabledLine:S,tabTextColorSegment:_,tabTextColorActiveSegment:o,tabTextColorHoverSegment:o,tabTextColorDisabledSegment:S,tabTextColorBar:_,tabTextColorActiveBar:s,tabTextColorHoverBar:s,tabTextColorDisabledBar:S,tabTextColorCard:_,tabTextColorHoverCard:_,tabTextColorActiveCard:s,tabTextColorDisabledCard:S,barColor:s,closeIconColor:v,closeIconColorHover:y,closeIconColorPressed:T,closeColorHover:d,closeColorPressed:z,closeBorderRadius:L,tabColor:P,tabColorSegment:$,tabBorderColor:A,tabFontWeightActive:B,tabFontWeight:B,tabBorderRadius:L,paneTextColor:o,fontWeightStrong:N})}const Ga={common:Dt,self:Da},De=Gt("n-tabs"),ut={tab:[String,Number,Object,Function],name:{type:[String,Number],required:!0},disabled:Boolean,displayDirective:{type:String,default:"if"},closable:{type:Boolean,default:void 0},tabProps:Object,label:[String,Number,Object,Function]},at=pe({__TAB_PANE__:!0,name:"TabPane",alias:["TabPanel"],props:ut,slots:Object,setup(e){const o=ot(De,null);return o||Ut("tab-pane","`n-tab-pane` must be placed inside `n-tabs`."),{style:o.paneStyleRef,class:o.paneClassRef,mergedClsPrefix:o.mergedClsPrefixRef}},render(){return m("div",{class:[`${this.mergedClsPrefix}-tab-pane`,this.class],style:this.style},this.$slots)}}),Ua=Object.assign({internalLeftPadded:Boolean,internalAddable:Boolean,internalCreatedByPane:Boolean},Jt(ut,["displayDirective"])),He=pe({__TAB__:!0,inheritAttrs:!1,name:"Tab",props:Ua,setup(e){const{mergedClsPrefixRef:o,valueRef:s,typeRef:S,closableRef:v,tabStyleRef:y,addTabStyleRef:T,tabClassRef:d,addTabClassRef:z,tabChangeIdRef:P,onBeforeLeaveRef:$,triggerRef:A,handleAdd:B,activateTab:_,handleClose:L}=ot(De);return{trigger:A,mergedClosable:re(()=>{if(e.internalAddable)return!1;const{closable:W}=e;return W===void 0?v.value:W}),style:y,addStyle:T,tabClass:d,addTabClass:z,clsPrefix:o,value:s,type:S,handleClose(W){W.stopPropagation(),!e.disabled&&L(e.name)},activateTab(){if(e.disabled)return;if(e.internalAddable){B();return}const{name:W}=e,N=++P.id;if(W!==s.value){const{value:j}=$;j?Promise.resolve(j(e.name,s.value)).then(h=>{h&&P.id===N&&_(W)}):_(W)}}}},render(){const{internalAddable:e,clsPrefix:o,name:s,disabled:S,label:v,tab:y,value:T,mergedClosable:d,trigger:z,$slots:{default:P}}=this,$=v??y;return m("div",{class:`${o}-tabs-tab-wrapper`},this.internalLeftPadded?m("div",{class:`${o}-tabs-tab-pad`}):null,m("div",Object.assign({key:s,"data-name":s,"data-disabled":S?!0:void 0},Xt({class:[`${o}-tabs-tab`,T===s&&`${o}-tabs-tab--active`,S&&`${o}-tabs-tab--disabled`,d&&`${o}-tabs-tab--closable`,e&&`${o}-tabs-tab--addable`,e?this.addTabClass:this.tabClass],onClick:z==="click"?this.activateTab:void 0,onMouseenter:z==="hover"?this.activateTab:void 0,style:e?this.addStyle:this.style},this.internalCreatedByPane?this.tabProps||{}:this.$attrs)),m("span",{class:`${o}-tabs-tab__label`},e?m(it,null,m("div",{class:`${o}-tabs-tab__height-placeholder`}," "),m(qt,{clsPrefix:o},{default:()=>m(Ca,null)})):P?P():typeof $=="object"?$:Yt($??s)),d&&this.type==="card"?m(Kt,{clsPrefix:o,class:`${o}-tabs-tab__close`,onClick:this.handleClose,disabled:S}):null))}}),Xa=i("tabs",`
 box-sizing: border-box;
 width: 100%;
 display: flex;
 flex-direction: column;
 transition:
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
`,[p("segment-type",[i("tabs-rail",[E("&.transition-disabled",[i("tabs-capsule",`
 transition: none;
 `)])])]),p("top",[i("tab-pane",`
 padding: var(--n-pane-padding-top) var(--n-pane-padding-right) var(--n-pane-padding-bottom) var(--n-pane-padding-left);
 `)]),p("left",[i("tab-pane",`
 padding: var(--n-pane-padding-right) var(--n-pane-padding-bottom) var(--n-pane-padding-left) var(--n-pane-padding-top);
 `)]),p("left, right",`
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
 `)]),p("right",`
 flex-direction: row-reverse;
 `,[i("tab-pane",`
 padding: var(--n-pane-padding-left) var(--n-pane-padding-top) var(--n-pane-padding-right) var(--n-pane-padding-bottom);
 `),i("tabs-bar",`
 left: 0;
 `)]),p("bottom",`
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
 `,[p("active",`
 font-weight: var(--n-font-weight-strong);
 color: var(--n-tab-text-color-active);
 `),E("&:hover",`
 color: var(--n-tab-text-color-hover);
 `)])])]),p("flex",[i("tabs-nav",`
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
 `),F("prefix","padding-right: 16px;"),F("suffix","padding-left: 16px;")]),p("top, bottom",[E(">",[i("tabs-nav",[i("tabs-nav-scroll-wrapper",[E("&::before",`
 top: 0;
 bottom: 0;
 left: 0;
 width: 20px;
 `),E("&::after",`
 top: 0;
 bottom: 0;
 right: 0;
 width: 20px;
 `),p("shadow-start",[E("&::before",`
 box-shadow: inset 10px 0 8px -8px rgba(0, 0, 0, .12);
 `)]),p("shadow-end",[E("&::after",`
 box-shadow: inset -10px 0 8px -8px rgba(0, 0, 0, .12);
 `)])])])])]),p("left, right",[i("tabs-nav-scroll-content",`
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
 `),p("shadow-start",[E("&::before",`
 box-shadow: inset 0 10px 8px -8px rgba(0, 0, 0, .12);
 `)]),p("shadow-end",[E("&::after",`
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
 `,[p("disabled",{cursor:"not-allowed"}),F("close",`
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
 `),p("disabled",`
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
 `),p("line-type, bar-type",[i("tabs-tab",`
 font-weight: var(--n-tab-font-weight);
 box-sizing: border-box;
 vertical-align: bottom;
 `,[E("&:hover",{color:"var(--n-tab-text-color-hover)"}),p("active",`
 color: var(--n-tab-text-color-active);
 font-weight: var(--n-tab-font-weight-active);
 `),p("disabled",{color:"var(--n-tab-text-color-disabled)"})])]),i("tabs-nav",[p("line-type",[p("top",[F("prefix, suffix",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),i("tabs-nav-scroll-content",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),i("tabs-bar",`
 bottom: -1px;
 `)]),p("left",[F("prefix, suffix",`
 border-right: 1px solid var(--n-tab-border-color);
 `),i("tabs-nav-scroll-content",`
 border-right: 1px solid var(--n-tab-border-color);
 `),i("tabs-bar",`
 right: -1px;
 `)]),p("right",[F("prefix, suffix",`
 border-left: 1px solid var(--n-tab-border-color);
 `),i("tabs-nav-scroll-content",`
 border-left: 1px solid var(--n-tab-border-color);
 `),i("tabs-bar",`
 left: -1px;
 `)]),p("bottom",[F("prefix, suffix",`
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
 `)]),p("card-type",[F("prefix, suffix",`
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
 `,[p("addable",`
 padding-left: 8px;
 padding-right: 8px;
 font-size: 16px;
 justify-content: center;
 `,[F("height-placeholder",`
 width: 0;
 font-size: var(--n-tab-font-size);
 `),Zt("disabled",[E("&:hover",`
 color: var(--n-tab-text-color-hover);
 `)])]),p("closable","padding-right: 8px;"),p("active",`
 background-color: #0000;
 font-weight: var(--n-tab-font-weight-active);
 color: var(--n-tab-text-color-active);
 `),p("disabled","color: var(--n-tab-text-color-disabled);")])]),p("left, right",`
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
 `)])]),p("top",[p("card-type",[i("tabs-scroll-padding","border-bottom: 1px solid var(--n-tab-border-color);"),F("prefix, suffix",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),i("tabs-tab",`
 border-top-left-radius: var(--n-tab-border-radius);
 border-top-right-radius: var(--n-tab-border-radius);
 `,[p("active",`
 border-bottom: 1px solid #0000;
 `)]),i("tabs-tab-pad",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),i("tabs-pad",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `)])]),p("left",[p("card-type",[i("tabs-scroll-padding","border-right: 1px solid var(--n-tab-border-color);"),F("prefix, suffix",`
 border-right: 1px solid var(--n-tab-border-color);
 `),i("tabs-tab",`
 border-top-left-radius: var(--n-tab-border-radius);
 border-bottom-left-radius: var(--n-tab-border-radius);
 `,[p("active",`
 border-right: 1px solid #0000;
 `)]),i("tabs-tab-pad",`
 border-right: 1px solid var(--n-tab-border-color);
 `),i("tabs-pad",`
 border-right: 1px solid var(--n-tab-border-color);
 `)])]),p("right",[p("card-type",[i("tabs-scroll-padding","border-left: 1px solid var(--n-tab-border-color);"),F("prefix, suffix",`
 border-left: 1px solid var(--n-tab-border-color);
 `),i("tabs-tab",`
 border-top-right-radius: var(--n-tab-border-radius);
 border-bottom-right-radius: var(--n-tab-border-radius);
 `,[p("active",`
 border-left: 1px solid #0000;
 `)]),i("tabs-tab-pad",`
 border-left: 1px solid var(--n-tab-border-color);
 `),i("tabs-pad",`
 border-left: 1px solid var(--n-tab-border-color);
 `)])]),p("bottom",[p("card-type",[i("tabs-scroll-padding","border-top: 1px solid var(--n-tab-border-color);"),F("prefix, suffix",`
 border-top: 1px solid var(--n-tab-border-color);
 `),i("tabs-tab",`
 border-bottom-left-radius: var(--n-tab-border-radius);
 border-bottom-right-radius: var(--n-tab-border-radius);
 `,[p("active",`
 border-top: 1px solid #0000;
 `)]),i("tabs-tab-pad",`
 border-top: 1px solid var(--n-tab-border-color);
 `),i("tabs-pad",`
 border-top: 1px solid var(--n-tab-border-color);
 `)])])])]),Fe=Oa,qa=Object.assign(Object.assign({},st.props),{value:[String,Number],defaultValue:[String,Number],trigger:{type:String,default:"click"},type:{type:String,default:"bar"},closable:Boolean,justifyContent:String,size:String,placement:{type:String,default:"top"},tabStyle:[String,Object],tabClass:String,addTabStyle:[String,Object],addTabClass:String,barWidth:Number,paneClass:String,paneStyle:[String,Object],paneWrapperClass:String,paneWrapperStyle:[String,Object],addable:[Boolean,Object],tabsPadding:{type:Number,default:0},animated:Boolean,onBeforeLeave:Function,onAdd:Function,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],onClose:[Function,Array],labelSize:String,activeName:[String,Number],onActiveNameChange:[Function,Array]}),Ya=pe({name:"Tabs",props:qa,slots:Object,setup(e,{slots:o}){var s,S,v,y;const{mergedClsPrefixRef:T,inlineThemeDisabled:d,mergedComponentPropsRef:z}=Qt(e),P=st("Tabs","-tabs",Xa,Ga,e,T),$=w(null),A=w(null),B=w(null),_=w(null),L=w(null),W=w(null),N=w(!0),j=w(!0),h=qe(e,["labelSize","size"]),R=re(()=>{var r,n;if(h.value)return h.value;const c=(n=(r=z==null?void 0:z.value)===null||r===void 0?void 0:r.Tabs)===null||n===void 0?void 0:n.size;return c||"medium"}),O=qe(e,["activeName","value"]),C=w((S=(s=O.value)!==null&&s!==void 0?s:e.defaultValue)!==null&&S!==void 0?S:o.default?(y=(v=We(o.default())[0])===null||v===void 0?void 0:v.props)===null||y===void 0?void 0:y.name:null),f=ea(O,C),M={id:0},U=re(()=>{if(!(!e.justifyContent||e.type==="card"))return{display:"flex",justifyContent:e.justifyContent}});_e(f,()=>{M.id=0,ne(),ge()});function D(){var r;const{value:n}=f;return n===null?null:(r=$.value)===null||r===void 0?void 0:r.querySelector(`[data-name="${n}"]`)}function ae(r){if(e.type==="card")return;const{value:n}=A;if(!n)return;const c=n.style.opacity==="0";if(r){const x=`${T.value}-tabs-bar--disabled`,{barWidth:I,placement:X}=e;if(r.dataset.disabled==="true"?n.classList.add(x):n.classList.remove(x),["top","bottom"].includes(X)){if(ve(["top","maxHeight","height"]),typeof I=="number"&&r.offsetWidth>=I){const q=Math.floor((r.offsetWidth-I)/2)+r.offsetLeft;n.style.left=`${q}px`,n.style.maxWidth=`${I}px`}else n.style.left=`${r.offsetLeft}px`,n.style.maxWidth=`${r.offsetWidth}px`;n.style.width="8192px",c&&(n.style.transition="none"),n.offsetWidth,c&&(n.style.transition="",n.style.opacity="1")}else{if(ve(["left","maxWidth","width"]),typeof I=="number"&&r.offsetHeight>=I){const q=Math.floor((r.offsetHeight-I)/2)+r.offsetTop;n.style.top=`${q}px`,n.style.maxHeight=`${I}px`}else n.style.top=`${r.offsetTop}px`,n.style.maxHeight=`${r.offsetHeight}px`;n.style.height="8192px",c&&(n.style.transition="none"),n.offsetHeight,c&&(n.style.transition="",n.style.opacity="1")}}}function Te(){if(e.type==="card")return;const{value:r}=A;r&&(r.style.opacity="0")}function ve(r){const{value:n}=A;if(n)for(const c of r)n.style[c]=""}function ne(){if(e.type==="card")return;const r=D();r?ae(r):Te()}function ge(){var r;const n=(r=L.value)===null||r===void 0?void 0:r.$el;if(!n)return;const c=D();if(!c)return;const{scrollLeft:x,offsetWidth:I}=n,{offsetLeft:X,offsetWidth:q}=c;x>X?n.scrollTo({top:0,left:X,behavior:"smooth"}):X+q>x+I&&n.scrollTo({top:0,left:X+q-I,behavior:"smooth"})}const le=w(null);let ue=0,G=null;function ze(r){const n=le.value;if(n){ue=r.getBoundingClientRect().height;const c=`${ue}px`,x=()=>{n.style.height=c,n.style.maxHeight=c};G?(x(),G(),G=null):G=x}}function Pe(r){const n=le.value;if(n){const c=r.getBoundingClientRect().height,x=()=>{document.body.offsetHeight,n.style.maxHeight=`${c}px`,n.style.height=`${Math.max(ue,c)}px`};G?(G(),G=null,x()):G=x}}function Re(){const r=le.value;if(r){r.style.maxHeight="",r.style.height="";const{paneWrapperStyle:n}=e;if(typeof n=="string")r.style.cssText=n;else if(n){const{maxHeight:c,height:x}=n;c!==void 0&&(r.style.maxHeight=c),x!==void 0&&(r.style.height=x)}}}const me={value:[]},he=w("next");function $e(r){const n=f.value;let c="next";for(const x of me.value){if(x===n)break;if(x===r){c="prev";break}}he.value=c,Le(r)}function Le(r){const{onActiveNameChange:n,onUpdateValue:c,"onUpdate:value":x}=e;n&&Ce(n,r),c&&Ce(c,r),x&&Ce(x,r),C.value=r}function ke(r){const{onClose:n}=e;n&&Ce(n,r)}function a(){const{value:r}=A;if(!r)return;const n="transition-disabled";r.classList.add(n),ne(),r.classList.remove(n)}const t=w(null);function l({transitionDisabled:r}){const n=$.value;if(!n)return;r&&n.classList.add("transition-disabled");const c=D();c&&t.value&&(t.value.style.width=`${c.offsetWidth}px`,t.value.style.height=`${c.offsetHeight}px`,t.value.style.transform=`translateX(${c.offsetLeft-na(getComputedStyle(n).paddingLeft)}px)`,r&&t.value.offsetWidth),r&&n.classList.remove("transition-disabled")}_e([f],()=>{e.type==="segment"&&Ee(()=>{l({transitionDisabled:!1})})}),dt(()=>{e.type==="segment"&&l({transitionDisabled:!0})});let k=0;function V(r){var n;if(r.contentRect.width===0&&r.contentRect.height===0||k===r.contentRect.width)return;k=r.contentRect.width;const{type:c}=e;if((c==="line"||c==="bar")&&a(),c!=="segment"){const{placement:x}=e;Be((x==="top"||x==="bottom"?(n=L.value)===null||n===void 0?void 0:n.$el:W.value)||null)}}const oe=Fe(V,64);_e([()=>e.justifyContent,()=>e.size],()=>{Ee(()=>{const{type:r}=e;(r==="line"||r==="bar")&&a()})});const Q=w(!1);function ct(r){var n;const{target:c,contentRect:{width:x,height:I}}=r,X=c.parentElement.parentElement.offsetWidth,q=c.parentElement.parentElement.offsetHeight,{placement:se}=e;if(!Q.value)se==="top"||se==="bottom"?X<x&&(Q.value=!0):q<I&&(Q.value=!0);else{const{value:ce}=_;if(!ce)return;se==="top"||se==="bottom"?X-x>ce.$el.offsetWidth&&(Q.value=!1):q-I>ce.$el.offsetHeight&&(Q.value=!1)}Be(((n=L.value)===null||n===void 0?void 0:n.$el)||null)}const bt=Fe(ct,64);function ft(){const{onAdd:r}=e;r&&r(),Ee(()=>{const n=D(),{value:c}=L;!n||!c||c.scrollTo({left:n.offsetLeft,top:0,behavior:"smooth"})})}function Be(r){if(!r)return;const{placement:n}=e;if(n==="top"||n==="bottom"){const{scrollLeft:c,scrollWidth:x,offsetWidth:I}=r;N.value=c<=0,j.value=c+I>=x}else{const{scrollTop:c,scrollHeight:x,offsetHeight:I}=r;N.value=c<=0,j.value=c+I>=x}}const pt=Fe(r=>{Be(r.target)},64);da(De,{triggerRef:J(e,"trigger"),tabStyleRef:J(e,"tabStyle"),tabClassRef:J(e,"tabClass"),addTabStyleRef:J(e,"addTabStyle"),addTabClassRef:J(e,"addTabClass"),paneClassRef:J(e,"paneClass"),paneStyleRef:J(e,"paneStyle"),mergedClsPrefixRef:T,typeRef:J(e,"type"),closableRef:J(e,"closable"),valueRef:f,tabChangeIdRef:M,onBeforeLeaveRef:J(e,"onBeforeLeave"),activateTab:$e,handleClose:ke,handleAdd:ft}),ta(()=>{ne(),ge()}),aa(()=>{const{value:r}=B;if(!r)return;const{value:n}=T,c=`${n}-tabs-nav-scroll-wrapper--shadow-start`,x=`${n}-tabs-nav-scroll-wrapper--shadow-end`;N.value?r.classList.remove(c):r.classList.add(c),j.value?r.classList.remove(x):r.classList.add(x)});const vt={syncBarPosition:()=>{ne()}},gt=()=>{l({transitionDisabled:!0})},Ge=re(()=>{const{value:r}=R,{type:n}=e,c={card:"Card",bar:"Bar",line:"Line",segment:"Segment"}[n],x=`${r}${c}`,{self:{barColor:I,closeIconColor:X,closeIconColorHover:q,closeIconColorPressed:se,tabColor:ce,tabBorderColor:mt,paneTextColor:ht,tabFontWeight:xt,tabBorderRadius:yt,tabFontWeightActive:Ct,colorSegment:St,fontWeightStrong:_t,tabColorSegment:wt,closeSize:Tt,closeIconSize:zt,closeColorHover:Pt,closeColorPressed:Rt,closeBorderRadius:$t,[K("panePadding",r)]:xe,[K("tabPadding",x)]:Lt,[K("tabPaddingVertical",x)]:kt,[K("tabGap",x)]:Bt,[K("tabGap",`${x}Vertical`)]:Wt,[K("tabTextColor",n)]:At,[K("tabTextColorActive",n)]:Et,[K("tabTextColorHover",n)]:Nt,[K("tabTextColorDisabled",n)]:It,[K("tabFontSize",r)]:jt},common:{cubicBezierEaseInOut:Mt}}=P.value;return{"--n-bezier":Mt,"--n-color-segment":St,"--n-bar-color":I,"--n-tab-font-size":jt,"--n-tab-text-color":At,"--n-tab-text-color-active":Et,"--n-tab-text-color-disabled":It,"--n-tab-text-color-hover":Nt,"--n-pane-text-color":ht,"--n-tab-border-color":mt,"--n-tab-border-radius":yt,"--n-close-size":Tt,"--n-close-icon-size":zt,"--n-close-color-hover":Pt,"--n-close-color-pressed":Rt,"--n-close-border-radius":$t,"--n-close-icon-color":X,"--n-close-icon-color-hover":q,"--n-close-icon-color-pressed":se,"--n-tab-color":ce,"--n-tab-font-weight":xt,"--n-tab-font-weight-active":Ct,"--n-tab-padding":Lt,"--n-tab-padding-vertical":kt,"--n-tab-gap":Bt,"--n-tab-gap-vertical":Wt,"--n-pane-padding-left":ye(xe,"left"),"--n-pane-padding-right":ye(xe,"right"),"--n-pane-padding-top":ye(xe,"top"),"--n-pane-padding-bottom":ye(xe,"bottom"),"--n-font-weight-strong":_t,"--n-tab-color-segment":wt}}),ie=d?ra("tabs",re(()=>`${R.value[0]}${e.type[0]}`),Ge,e):void 0;return Object.assign({mergedClsPrefix:T,mergedValue:f,renderedNames:new Set,segmentCapsuleElRef:t,tabsPaneWrapperRef:le,tabsElRef:$,barElRef:A,addTabInstRef:_,xScrollInstRef:L,scrollWrapperElRef:B,addTabFixed:Q,tabWrapperStyle:U,handleNavResize:oe,mergedSize:R,handleScroll:pt,handleTabsResize:bt,cssVars:d?void 0:Ge,themeClass:ie==null?void 0:ie.themeClass,animationDirection:he,renderNameListRef:me,yScrollElRef:W,handleSegmentResize:gt,onAnimationBeforeLeave:ze,onAnimationEnter:Pe,onAnimationAfterEnter:Re,onRender:ie==null?void 0:ie.onRender},vt)},render(){const{mergedClsPrefix:e,type:o,placement:s,addTabFixed:S,addable:v,mergedSize:y,renderNameListRef:T,onRender:d,paneWrapperClass:z,paneWrapperStyle:P,$slots:{default:$,prefix:A,suffix:B}}=this;d==null||d();const _=$?We($()).filter(C=>C.type.__TAB_PANE__===!0):[],L=$?We($()).filter(C=>C.type.__TAB__===!0):[],W=!L.length,N=o==="card",j=o==="segment",h=!N&&!j&&this.justifyContent;T.value=[];const R=()=>{const C=m("div",{style:this.tabWrapperStyle,class:`${e}-tabs-wrapper`},h?null:m("div",{class:`${e}-tabs-scroll-padding`,style:s==="top"||s==="bottom"?{width:`${this.tabsPadding}px`}:{height:`${this.tabsPadding}px`}}),W?_.map((f,M)=>(T.value.push(f.props.name),Oe(m(He,Object.assign({},f.props,{internalCreatedByPane:!0,internalLeftPadded:M!==0&&(!h||h==="center"||h==="start"||h==="end")}),f.children?{default:f.children.tab}:void 0)))):L.map((f,M)=>(T.value.push(f.props.name),Oe(M!==0&&!h?lt(f):f))),!S&&v&&N?nt(v,(W?_.length:L.length)!==0):null,h?null:m("div",{class:`${e}-tabs-scroll-padding`,style:{width:`${this.tabsPadding}px`}}));return m("div",{ref:"tabsElRef",class:`${e}-tabs-nav-scroll-content`},N&&v?m(Ae,{onResize:this.handleTabsResize},{default:()=>C}):C,N?m("div",{class:`${e}-tabs-pad`}):null,N?null:m("div",{ref:"barElRef",class:`${e}-tabs-bar`}))},O=j?"top":s;return m("div",{class:[`${e}-tabs`,this.themeClass,`${e}-tabs--${o}-type`,`${e}-tabs--${y}-size`,h&&`${e}-tabs--flex`,`${e}-tabs--${O}`],style:this.cssVars},m("div",{class:[`${e}-tabs-nav--${o}-type`,`${e}-tabs-nav--${O}`,`${e}-tabs-nav`]},Xe(A,C=>C&&m("div",{class:`${e}-tabs-nav__prefix`},C)),j?m(Ae,{onResize:this.handleSegmentResize},{default:()=>m("div",{class:`${e}-tabs-rail`,ref:"tabsElRef"},m("div",{class:`${e}-tabs-capsule`,ref:"segmentCapsuleElRef"},m("div",{class:`${e}-tabs-wrapper`},m("div",{class:`${e}-tabs-tab`}))),W?_.map((C,f)=>(T.value.push(C.props.name),m(He,Object.assign({},C.props,{internalCreatedByPane:!0,internalLeftPadded:f!==0}),C.children?{default:C.children.tab}:void 0))):L.map((C,f)=>(T.value.push(C.props.name),f===0?C:lt(C))))}):m(Ae,{onResize:this.handleNavResize},{default:()=>m("div",{class:`${e}-tabs-nav-scroll-wrapper`,ref:"scrollWrapperElRef"},["top","bottom"].includes(O)?m(Ra,{ref:"xScrollInstRef",onScroll:this.handleScroll},{default:R}):m("div",{class:`${e}-tabs-nav-y-scroll`,onScroll:this.handleScroll,ref:"yScrollElRef"},R()))}),S&&v&&N?nt(v,!0):null,Xe(B,C=>C&&m("div",{class:`${e}-tabs-nav__suffix`},C))),W&&(this.animated&&(O==="top"||O==="bottom")?m("div",{ref:"tabsPaneWrapperRef",style:P,class:[`${e}-tabs-pane-wrapper`,z]},rt(_,this.mergedValue,this.renderedNames,this.onAnimationBeforeLeave,this.onAnimationEnter,this.onAnimationAfterEnter,this.animationDirection)):rt(_,this.mergedValue,this.renderedNames)))}});function rt(e,o,s,S,v,y,T){const d=[];return e.forEach(z=>{const{name:P,displayDirective:$,"display-directive":A}=z.props,B=L=>$===L||A===L,_=o===P;if(z.key!==void 0&&(z.key=P),_||B("show")||B("show:lazy")&&s.has(P)){s.has(P)||s.add(P);const L=!B("if");d.push(L?la(z,[[oa,_]]):z)}}),T?m(ia,{name:`${T}-transition`,onBeforeLeave:S,onEnter:v,onAfterEnter:y},{default:()=>d}):d}function nt(e,o){return m(He,{ref:"addTabInstRef",key:"__addable",name:"__addable",internalCreatedByPane:!0,internalAddable:!0,internalLeftPadded:o,disabled:typeof e=="object"&&e.disabled})}function lt(e){const o=sa(e);return o.props?o.props.internalLeftPadded=!0:o.props={internalLeftPadded:!0},o}function Oe(e){return Array.isArray(e.dynamicProps)?e.dynamicProps.includes("internalLeftPadded")||e.dynamicProps.push("internalLeftPadded"):e.dynamicProps=["internalLeftPadded"],e}const te={list:()=>ee.get("/suites"),get:e=>ee.get(`/suites/${e}`),create:e=>ee.post("/suites",e),update:(e,o)=>ee.put(`/suites/${e}`,o),delete:e=>ee.delete(`/suites/${e}`),run:(e,o)=>ee.post(`/suites/${e}/runs`,o),listRuns:e=>ee.get(`/suites/${e}/runs`),getRun:(e,o)=>ee.get(`/suites/${e}/runs/${o}`)},Ka={style:{color:"#999","font-size":"13px"}},Ja={style:{"font-weight":"600","margin-bottom":"8px"}},Za={style:{color:"#999","font-size":"13px","font-weight":"normal"}},mr=pe({__name:"SuiteCenter",setup(e){const o=ga(),s=Sa(),{setPageSummary:S,clearPageSummary:v}=ca(),y=w([]),T=w(!1),d=w(null),z=w([]),P=w(!1),$=w(!1),A=w(!1),B=w(!1),_=w(null),L=w(null),W=w([]),N=w([]),j=w({}),h=w({target_app_id:"",environment:"",override_host:"",concurrency:void 0,perf_threshold_ms:void 0}),R=w({name:"",description:"",default_target_app_id:void 0,default_environment:"",default_concurrency:1,default_delay_ms:0,default_perf_threshold_ms:void 0}),O=w(""),C=w(null),f=w("descend"),M=xa(),U=re(()=>{let a=y.value;if(O.value){const t=O.value.toLowerCase();a=a.filter(l=>l.name.toLowerCase().includes(t))}return C.value&&(a=a.filter(t=>ya(t.created_at,C.value))),a=[...a].sort((t,l)=>{const k=new Date(t.created_at).getTime()-new Date(l.created_at).getTime();return f.value==="ascend"?k:-k}),a}),D=Ke({page:1,pageSize:10,showSizePicker:!0,pageSizes:[10,20,50],onChange:a=>{D.page=a},onUpdatePageSize:a=>{D.pageSize=a,D.page=1}}),ae=Ke({page:1,pageSize:10,showSizePicker:!0,pageSizes:[10,20,50],onChange:a=>{ae.page=a},onUpdatePageSize:a=>{ae.pageSize=a,ae.page=1}}),Te=a=>a>=.9?"#18a058":a>=.6?"#f0a020":"#d03050",ve=re(()=>[{title:"名称",key:"name"},{title:"用例数",key:"case_count",render:a=>{var t;return((t=a.case_ids)==null?void 0:t.length)??0}},{title:"默认环境",key:"default_environment",render:a=>a.default_environment||"-"},{title:"创建时间",key:"created_at",sorter:!0,sortOrder:f.value,render:a=>Je(a.created_at)},{title:"操作",key:"actions",width:120,render:a=>m(Z,{size:"small",onClick:()=>ze(a)},()=>"查看/执行")}]);function ne(){O.value="",C.value=null}function ge(a){(a==null?void 0:a.columnKey)==="created_at"&&(f.value=a.order||"descend")}const le=[{title:"状态",key:"status",width:90,render:a=>m("span",{style:`color:${a.status==="DONE"?"#18a058":a.status==="FAILED"?"#d03050":"#f0a020"}`},a.status==="DONE"?"已完成":a.status==="FAILED"?"失败":"运行中")},{title:"用例",key:"cases",render:a=>`${a.passed_cases}/${a.total_cases} 通过`},{title:"通过率",key:"rate",render:a=>{const t=Math.round((a.overall_pass_rate??0)*100);return m("span",{style:`color:${Te(a.overall_pass_rate??0)};font-weight:bold`},`${t}%`)}},{title:"开始时间",key:"started_at",render:a=>Je(a.started_at)},{title:"操作",key:"actions",width:120,render:a=>{var t;return(t=a.job_ids)!=null&&t.length?m(Z,{size:"small",onClick:()=>o.push(`/results/${a.job_ids[0]}`)},()=>"查看第1个任务"):"-"}}];async function ue(){T.value=!0;try{const a=await te.list();y.value=a.data}finally{T.value=!1}}async function G(a){P.value=!0;try{const t=await te.listRuns(a);z.value=t.data}finally{P.value=!1}}function ze(a){d.value=a,ae.page=1,h.value={target_app_id:a.default_target_app_id||"",environment:a.default_environment||"",override_host:a.default_override_host||"",concurrency:void 0,perf_threshold_ms:a.default_perf_threshold_ms??void 0},G(a.id)}function Pe(){_.value=null,R.value={name:"",description:"",default_target_app_id:void 0,default_environment:"",default_concurrency:1,default_delay_ms:0,default_perf_threshold_ms:void 0},B.value=!0}function Re(a){_.value=a.id,R.value={name:a.name,description:a.description||"",default_target_app_id:a.default_target_app_id||void 0,default_environment:a.default_environment||"",default_concurrency:a.default_concurrency??1,default_delay_ms:a.default_delay_ms??0,default_perf_threshold_ms:a.default_perf_threshold_ms??void 0},B.value=!0}async function me(){var a,t,l;if(!R.value.name){s.warning("请填写套件名称");return}A.value=!0;try{const k={...R.value};if(k.default_environment||delete k.default_environment,k.description||delete k.description,k.default_perf_threshold_ms||delete k.default_perf_threshold_ms,_.value){const V=await te.update(_.value,k),oe=y.value.findIndex(Q=>Q.id===_.value);oe>=0&&(y.value[oe]=V.data),((a=d.value)==null?void 0:a.id)===_.value&&(d.value=V.data)}else{const V=await te.create(k);y.value.unshift(V.data)}B.value=!1,s.success("保存成功")}catch(k){s.error(((l=(t=k.response)==null?void 0:t.data)==null?void 0:l.detail)||"保存失败")}finally{A.value=!1}}async function he(a){var t,l,k;try{await te.delete(a),y.value=y.value.filter(V=>V.id!==a),((t=d.value)==null?void 0:t.id)===a&&(d.value=null),s.success("已删除")}catch(V){s.error(((k=(l=V.response)==null?void 0:l.data)==null?void 0:k.detail)||"删除失败")}}async function $e(){var a,t;if(d.value){if(!h.value.target_app_id){s.warning("请选择目标应用");return}$.value=!0;try{const l={target_app_id:h.value.target_app_id};h.value.environment&&(l.environment=h.value.environment),h.value.override_host&&(l.override_host=h.value.override_host),h.value.concurrency&&(l.concurrency=h.value.concurrency),h.value.perf_threshold_ms&&(l.perf_threshold_ms=h.value.perf_threshold_ms),await te.run(d.value.id,l),s.success("套件已开始执行"),await G(d.value.id)}catch(l){s.error(((t=(a=l.response)==null?void 0:a.data)==null?void 0:t.detail)||"执行失败")}finally{$.value=!1}}}async function Le(a){if(!a||!d.value)return;const t=d.value.case_ids||[];if(t.includes(a)){s.warning("用例已在套件中"),L.value=null;return}const l=[...t,a],k=await te.update(d.value.id,{case_ids:l});d.value=k.data;const V=y.value.findIndex(oe=>oe.id===d.value.id);V>=0&&(y.value[V]=k.data),L.value=null,s.success("已添加")}async function ke(a){if(!d.value)return;const t=(d.value.case_ids||[]).filter(V=>V!==a),l=await te.update(d.value.id,{case_ids:t});d.value=l.data;const k=y.value.findIndex(V=>V.id===d.value.id);k>=0&&(y.value[k]=l.data)}return dt(async()=>{const[a,t]=await Promise.all([ma.list(),ha.listAll()]);W.value=a.data.map(l=>({label:l.name,value:l.id})),N.value=t.map(l=>({label:l.name,value:l.id})),j.value=Object.fromEntries(t.map(l=>[l.id,l.name])),await ue()}),_e(()=>U.value.length,a=>{S(`共 ${a} 条套件`)},{immediate:!0}),ua(v),(a,t)=>(Se(),Ne(u(be),{vertical:"",size:16},{default:g(()=>[b(u(Ye),{title:"回放套件"},{"header-extra":g(()=>[b(u(be),{wrap:""},{default:g(()=>[b(u(de),{value:O.value,"onUpdate:value":t[0]||(t[0]=l=>O.value=l),placeholder:"搜索套件名称",clearable:"",style:{width:"180px"}},null,8,["value"]),b(u(_a),{value:C.value,"onUpdate:value":t[1]||(t[1]=l=>C.value=l),type:"datetimerange",clearable:"",shortcuts:u(M),style:{width:"320px"},"start-placeholder":"创建开始时间","end-placeholder":"创建结束时间"},null,8,["value","shortcuts"]),b(u(Z),{size:"small",onClick:ne},{default:g(()=>[...t[20]||(t[20]=[Y("清空筛选",-1)])]),_:1}),b(u(Z),{type:"primary",size:"small",onClick:Pe},{default:g(()=>[...t[21]||(t[21]=[Y("+ 新建套件",-1)])]),_:1})]),_:1})]),default:g(()=>[b(u(be),{align:"center",style:{"margin-bottom":"10px"}},{default:g(()=>[Ie("span",Ka,"共 "+je(U.value.length)+" 条",1)]),_:1}),b(u(Ze),{columns:ve.value,data:U.value,loading:T.value,"row-key":l=>l.id,pagination:D,"onUpdate:sorter":ge},null,8,["columns","data","loading","row-key","pagination"])]),_:1}),d.value?(Se(),Ne(u(Ye),{key:0,title:`套件：${d.value.name}`},{"header-extra":g(()=>[b(u(be),null,{default:g(()=>[b(u(Z),{size:"small",onClick:t[2]||(t[2]=l=>Re(d.value))},{default:g(()=>[...t[22]||(t[22]=[Y("编辑",-1)])]),_:1}),b(u(Ta),{onPositiveClick:t[3]||(t[3]=l=>he(d.value.id))},{trigger:g(()=>[b(u(Z),{size:"small",type:"error"},{default:g(()=>[...t[23]||(t[23]=[Y("删除",-1)])]),_:1})]),default:g(()=>[t[24]||(t[24]=Y(" 确认删除套件？ ",-1))]),_:1})]),_:1})]),default:g(()=>[b(u(Ya),{type:"line",animated:""},{default:g(()=>[b(u(at),{name:"run",tab:"执行套件"},{default:g(()=>[b(u(Qe),{"label-placement":"left","label-width":"130px",style:{"max-width":"560px","margin-top":"12px"}},{default:g(()=>[b(u(H),{label:"回放目标应用",required:""},{default:g(()=>[b(u(Me),{value:h.value.target_app_id,"onUpdate:value":t[4]||(t[4]=l=>h.value.target_app_id=l),options:W.value,placeholder:"选择目标应用"},null,8,["value","options"])]),_:1}),b(u(H),{label:"环境标签"},{default:g(()=>[b(u(de),{value:h.value.environment,"onUpdate:value":t[5]||(t[5]=l=>h.value.environment=l),placeholder:"staging / test（留空用套件默认）"},null,8,["value"])]),_:1}),b(u(H),{label:"Host 覆盖"},{default:g(()=>[b(u(de),{value:h.value.override_host,"onUpdate:value":t[6]||(t[6]=l=>h.value.override_host=l),placeholder:"留空用套件默认"},null,8,["value"])]),_:1}),b(u(H),{label:"并发数"},{default:g(()=>[b(u(fe),{value:h.value.concurrency,"onUpdate:value":t[7]||(t[7]=l=>h.value.concurrency=l),min:1,max:20,placeholder:"留空用套件默认"},null,8,["value"])]),_:1}),b(u(H),{label:"性能阈值(ms)"},{default:g(()=>[b(u(fe),{value:h.value.perf_threshold_ms,"onUpdate:value":t[8]||(t[8]=l=>h.value.perf_threshold_ms=l),min:0,placeholder:"超过此耗时标记 PERF FAIL"},null,8,["value"])]),_:1}),b(u(H),null,{default:g(()=>[b(u(Z),{type:"primary",loading:$.value,onClick:$e},{default:g(()=>[...t[25]||(t[25]=[Y("执行套件",-1)])]),_:1},8,["loading"])]),_:1})]),_:1}),b(u(wa)),Ie("div",Ja,[t[26]||(t[26]=Y("执行历史 ",-1)),Ie("span",Za,"共 "+je(z.value.length)+" 条",1)]),b(u(Ze),{columns:le,data:z.value,loading:P.value,size:"small",pagination:ae},null,8,["data","loading","pagination"]),b(u(Z),{size:"tiny",style:{"margin-top":"8px"},onClick:t[9]||(t[9]=l=>G(d.value.id))},{default:g(()=>[...t[27]||(t[27]=[Y("刷新",-1)])]),_:1})]),_:1}),b(u(at),{name:"cases",tab:"包含用例"},{default:g(()=>[b(u(be),{vertical:"",size:8,style:{"margin-top":"12px"}},{default:g(()=>[(Se(!0),ba(it,null,fa(d.value.case_ids,l=>(Se(),Ne(u(za),{key:l,closable:"",onClose:k=>ke(l)},{default:g(()=>[Y(je(j.value[l]||l.slice(0,8)),1)]),_:2},1032,["onClose"]))),128)),b(u(Me),{value:L.value,"onUpdate:value":[t[10]||(t[10]=l=>L.value=l),Le],options:N.value,filterable:"",clearable:"",placeholder:"添加测试用例",style:{width:"300px"}},null,8,["value","options"])]),_:1})]),_:1})]),_:1})]),_:1},8,["title"])):pa("",!0),b(u(va),{show:B.value,"onUpdate:show":t[19]||(t[19]=l=>B.value=l),preset:"dialog",title:_.value?"编辑套件":"新建套件",style:{width:"520px"}},{action:g(()=>[b(u(Z),{onClick:t[18]||(t[18]=l=>B.value=!1)},{default:g(()=>[...t[28]||(t[28]=[Y("取消",-1)])]),_:1}),b(u(Z),{type:"primary",loading:A.value,onClick:me},{default:g(()=>[...t[29]||(t[29]=[Y("保存",-1)])]),_:1},8,["loading"])]),default:g(()=>[b(u(Qe),{model:R.value,"label-placement":"left","label-width":"130px"},{default:g(()=>[b(u(H),{label:"套件名称",required:""},{default:g(()=>[b(u(de),{value:R.value.name,"onUpdate:value":t[11]||(t[11]=l=>R.value.name=l),placeholder:"如：用户模块回归测试"},null,8,["value"])]),_:1}),b(u(H),{label:"描述"},{default:g(()=>[b(u(de),{value:R.value.description,"onUpdate:value":t[12]||(t[12]=l=>R.value.description=l),type:"textarea",rows:2},null,8,["value"])]),_:1}),b(u(H),{label:"默认目标应用"},{default:g(()=>[b(u(Me),{value:R.value.default_target_app_id,"onUpdate:value":t[13]||(t[13]=l=>R.value.default_target_app_id=l),options:W.value,clearable:"",placeholder:"运行时可覆盖"},null,8,["value","options"])]),_:1}),b(u(H),{label:"默认环境"},{default:g(()=>[b(u(de),{value:R.value.default_environment,"onUpdate:value":t[14]||(t[14]=l=>R.value.default_environment=l),placeholder:"staging"},null,8,["value"])]),_:1}),b(u(H),{label:"默认并发数"},{default:g(()=>[b(u(fe),{value:R.value.default_concurrency,"onUpdate:value":t[15]||(t[15]=l=>R.value.default_concurrency=l),min:1,max:20},null,8,["value"])]),_:1}),b(u(H),{label:"默认延迟(ms)"},{default:g(()=>[b(u(fe),{value:R.value.default_delay_ms,"onUpdate:value":t[16]||(t[16]=l=>R.value.default_delay_ms=l),min:0},null,8,["value"])]),_:1}),b(u(H),{label:"默认性能阈值(ms)"},{default:g(()=>[b(u(fe),{value:R.value.default_perf_threshold_ms,"onUpdate:value":t[17]||(t[17]=l=>R.value.default_perf_threshold_ms=l),min:0,clearable:"",placeholder:"不限制"},null,8,["value"])]),_:1})]),_:1},8,["model"])]),_:1},8,["show","title"])]),_:1}))}});export{mr as default};
