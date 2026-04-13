import{p as y,s as B,v as C,d as S,n as g,I as z,J as b,M as T,m as f,bc as W,at as P}from"./index-By7nBA3K.js";const F={headerFontSize1:"30px",headerFontSize2:"22px",headerFontSize3:"18px",headerFontSize4:"16px",headerFontSize5:"16px",headerFontSize6:"16px",headerMargin1:"28px 0 20px 0",headerMargin2:"28px 0 20px 0",headerMargin3:"28px 0 20px 0",headerMargin4:"28px 0 18px 0",headerMargin5:"28px 0 18px 0",headerMargin6:"28px 0 18px 0",headerPrefixWidth1:"16px",headerPrefixWidth2:"16px",headerPrefixWidth3:"12px",headerPrefixWidth4:"12px",headerPrefixWidth5:"12px",headerPrefixWidth6:"12px",headerBarWidth1:"4px",headerBarWidth2:"4px",headerBarWidth3:"3px",headerBarWidth4:"3px",headerBarWidth5:"3px",headerBarWidth6:"3px",pMargin:"16px 0 16px 0",liMargin:".25em 0 0 0",olPadding:"0 0 0 2em",ulPadding:"0 0 0 2em"};function M(t){const{primaryColor:r,textColor2:o,borderColor:i,lineHeight:a,fontSize:e,borderRadiusSmall:l,dividerColor:d,fontWeightStrong:u,textColor1:n,textColor3:s,infoColor:c,warningColor:h,errorColor:x,successColor:p,codeColor:m}=t;return Object.assign(Object.assign({},F),{aTextColor:r,blockquoteTextColor:o,blockquotePrefixColor:i,blockquoteLineHeight:a,blockquoteFontSize:e,codeBorderRadius:l,liTextColor:o,liLineHeight:a,liFontSize:e,hrColor:d,headerFontWeight:u,headerTextColor:n,pTextColor:o,pTextColor1Depth:n,pTextColor2Depth:o,pTextColor3Depth:s,pLineHeight:a,pFontSize:e,headerBarColor:r,headerBarColorPrimary:r,headerBarColorInfo:c,headerBarColorError:x,headerBarColorWarning:h,headerBarColorSuccess:p,textColor:o,textColor1Depth:n,textColor2Depth:o,textColor3Depth:s,textColorPrimary:r,textColorInfo:c,textColorSuccess:p,textColorWarning:h,textColorError:x,codeTextColor:o,codeColor:m,codeBorder:"1px solid #0000"})}const $={common:y,self:M},D=B("text",`
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
`,[C("strong",`
 font-weight: var(--n-font-weight-strong);
 `),C("italic",{fontStyle:"italic"}),C("underline",{textDecoration:"underline"}),C("code",`
 line-height: 1.4;
 display: inline-block;
 font-family: var(--n-font-famliy-mono);
 transition: 
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 box-sizing: border-box;
 padding: .05em .35em 0 .35em;
 border-radius: var(--n-code-border-radius);
 font-size: .9em;
 color: var(--n-code-text-color);
 background-color: var(--n-code-color);
 border: var(--n-code-border);
 `)]),R=Object.assign(Object.assign({},b.props),{code:Boolean,type:{type:String,default:"default"},delete:Boolean,strong:Boolean,italic:Boolean,underline:Boolean,depth:[String,Number],tag:String,as:{type:String,validator:()=>!0,default:void 0}}),V=S({name:"Text",props:R,setup(t){const{mergedClsPrefixRef:r,inlineThemeDisabled:o}=z(t),i=b("Typography","-text",D,$,t,r),a=f(()=>{const{depth:l,type:d}=t,u=d==="default"?l===void 0?"textColor":`textColor${l}Depth`:P("textColor",d),{common:{fontWeightStrong:n,fontFamilyMono:s,cubicBezierEaseInOut:c},self:{codeTextColor:h,codeBorderRadius:x,codeColor:p,codeBorder:m,[u]:v}}=i.value;return{"--n-bezier":c,"--n-text-color":v,"--n-font-weight-strong":n,"--n-font-famliy-mono":s,"--n-code-border-radius":x,"--n-code-text-color":h,"--n-code-color":p,"--n-code-border":m}}),e=o?T("text",f(()=>`${t.type[0]}${t.depth||""}`),a,t):void 0;return{mergedClsPrefix:r,compitableTag:W(t,["as","tag"]),cssVars:o?void 0:a,themeClass:e==null?void 0:e.themeClass,onRender:e==null?void 0:e.onRender}},render(){var t,r,o;const{mergedClsPrefix:i}=this;(t=this.onRender)===null||t===void 0||t.call(this);const a=[`${i}-text`,this.themeClass,{[`${i}-text--code`]:this.code,[`${i}-text--delete`]:this.delete,[`${i}-text--strong`]:this.strong,[`${i}-text--italic`]:this.italic,[`${i}-text--underline`]:this.underline}],e=(o=(r=this.$slots).default)===null||o===void 0?void 0:o.call(r);return this.code?g("code",{class:a,style:this.cssVars},this.delete?g("del",null,e):e):this.delete?g("del",{class:a,style:this.cssVars},e):g(this.compitableTag||"span",{class:a,style:this.cssVars},e)}});export{V as N,$ as t};
