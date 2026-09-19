(async()=>{const nav=$('hist');if(!nav||!window.claude)return;let db=null;try{db=await claude.use('db')}catch(e){}if(!db)return;
let list=[];try{const q=await db.collection('indice').orderBy('data','desc').limit(1000).get();list=q.docs.map(d=>d.data()).filter(x=>x&&x.data)}catch(e){return}
if(!list.some(x=>x.data===ED.data))list.push({data:ED.data,rotulo:ED.rotulo,fat:ED.fat});
list.sort((a,b)=>a.data<b.data?1:-1);if(list.length<2)return;
const latest=list[0].data,cache={[ED.data]:{body:REL0,D:D}};let cur=ED.data,busy=false;
const kf=v=>v==null?'':' · '+(v>=1000?'R$ '+br(v/1000,1).replace(/,0$/,'')+' mil':'R$ '+br(v));
nav.innerHTML=`<span class="hl">${ED.tipo==='semanal'?'Semanas anteriores':'Dias anteriores'}</span><div class="hc"><button id="hPrev" aria-label="Edição anterior">‹</button><select id="hSel" aria-label="Escolher edição"></select><button id="hNext" aria-label="Próxima edição">›</button></div><button id="hLast" class="hlast" hidden>Voltar para a mais recente</button>`;
const sel=$('hSel');list.forEach(x=>{const o=document.createElement('option');o.value=x.data;o.textContent=(x.rotulo||x.data)+kf(x.fat);sel.appendChild(o)});
function ui(){const i=list.findIndex(x=>x.data===cur);sel.value=cur;$('hPrev').disabled=i>=list.length-1;$('hNext').disabled=i<=0;$('hLast').hidden=cur===latest;nav.classList.toggle('old',cur!==latest)}
async function go(id){if(busy||id===cur)return;busy=true;nav.classList.add('loading');try{let e=cache[id];if(!e){const s=await db.doc('edicoes/'+id).get();if(!s.exists)throw 0;e=s.data();cache[id]=e}
 $('rel').innerHTML=e.body;D=e.D;drawAll();if(typeof drawSem==='function')drawSem();cur=id;ui();window.scrollTo({top:0})}catch(err){sel.value=cur;nav.classList.add('err');setTimeout(()=>nav.classList.remove('err'),2500)}finally{busy=false;nav.classList.remove('loading')}}
sel.onchange=()=>go(sel.value);$('hPrev').onclick=()=>{const i=list.findIndex(x=>x.data===cur);if(i<list.length-1)go(list[i+1].data)};
$('hNext').onclick=()=>{const i=list.findIndex(x=>x.data===cur);if(i>0)go(list[i-1].data)};$('hLast').onclick=()=>go(latest);
ui();nav.hidden=false})();
