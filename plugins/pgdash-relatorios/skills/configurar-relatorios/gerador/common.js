const tip=document.getElementById('tip');
const $=id=>document.getElementById(id);
function showTip(e,h){tip.innerHTML=h;tip.style.opacity=1;tip.style.left=Math.min(e.clientX+12,innerWidth-tip.offsetWidth-8)+'px';tip.style.top=(e.clientY-40)+'px'}
function hideTip(){tip.style.opacity=0}
const NS='http://www.w3.org/2000/svg';
function el(t,a,p){const n=document.createElementNS(NS,t);for(const k in a)n.setAttribute(k,a[k]);p&&p.appendChild(n);return n}
const br=(v,d=0)=>v.toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d});
const fmt=v=>'R$ '+br(v);
function hover(node,html){node.addEventListener('mousemove',e=>showTip(e,html));node.addEventListener('mouseleave',hideTip)}
var CH=[];addEventListener('resize',()=>{clearTimeout(window._rt);window._rt=setTimeout(()=>CH.forEach(f=>f()),120)});
function chart(id,fn){const s=$(id);if(!s)return;let lw=0;const run=()=>{if(!s.isConnected)return;const cs=getComputedStyle(s.parentNode),W=Math.max(300,Math.round(s.parentNode.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight)));if(W===lw)return;lw=W;s.innerHTML='';const H=fn(s,W,W<560);s.setAttribute('viewBox',`0 0 ${W} ${H}`);s.setAttribute('height',H)};run();CH.push(run)}
