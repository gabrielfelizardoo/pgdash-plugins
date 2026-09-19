function drawSem(){
const kk=v=>{const s=br(v/1000,1);return 'R$ '+(s.endsWith(',0')?s.slice(0,-2):s)+' mil'};
chart('chW8',(s,W,n)=>{const w=D.w8,H=190,L=8,B=34,T=24,max=Math.max(...w.map(x=>x[1]))*1.08,bw=(W-L)/w.length,y=v=>H-B-v/max*(H-B-T),avg=D.m4;
w.forEach(([d0,v],i)=>{const last=i===w.length-1,x0=L+i*bw+bw*.18,ww=bw*.64;el('rect',{x:x0,y:y(v),width:ww,height:H-B-y(v),rx:4,fill:last?'var(--acc)':'var(--s1soft)'},s);
 el('text',{x:x0+ww/2,y:y(v)-6,'text-anchor':'middle',style:last?'fill:var(--acc);font-weight:700':'fill:var(--ink2)'},s).textContent=n?br(v/1000,0):kk(v).replace('R$ ','');
 const dt=new Date(d0+'T12:00:00');el('text',{x:x0+ww/2,y:H-B+16,'text-anchor':'middle'},s).textContent=dt.getDate()+'/'+(dt.getMonth()+1);
 hover(el('rect',{x:L+i*bw,y:T,width:bw,height:H-B-T,fill:'transparent'},s),`<b>Semana de ${dt.getDate()}/${dt.getMonth()+1}</b><br>${fmt(v)}`)});
if(avg){el('line',{x1:L,x2:W,y1:y(avg),y2:y(avg),stroke:'var(--ink2)','stroke-dasharray':'4 4'},s)}
el('line',{x1:L,x2:W,y1:H-B,y2:H-B,stroke:'var(--axis)'},s);el('text',{x:W/2,y:H-2,'text-anchor':'middle'},s).textContent=n?'início da semana (R$ mil)':'semana que começa em';return H});
chart('chDow',(s,W,n)=>{const dd=D.dias,H=180,L=34,B=24,T=10,mx=Math.max(...dd.flatMap(x=>[x[1],x[2]])),st=mx>20000?10000:mx>8000?5000:2000,max=Math.ceil(mx/st)*st,gw=(W-L)/7,y=v=>H-B-v/max*(H-B-T),lb=['Seg','Ter','Qua','Qui','Sex','Sáb','Dom'];
for(let g=0;g<=max;g+=st){el('line',{x1:L,x2:W,y1:y(g),y2:y(g),stroke:'var(--grid)'},s);el('text',{x:L-6,y:y(g)+4,'text-anchor':'end'},s).textContent=g/1000}
dd.forEach(([d0,a,b],i)=>{const x0=L+i*gw,bw=gw*.34;el('rect',{x:x0+gw*.14,y:y(b),width:bw,height:H-B-y(b),rx:3,fill:'var(--axis)'},s);el('rect',{x:x0+gw*.14+bw+2,y:y(a),width:bw,height:H-B-y(a),rx:3,fill:'var(--acc)'},s);
 el('text',{x:x0+gw/2,y:H-6,'text-anchor':'middle',style:'fill:var(--ink2);font-weight:600'},s).textContent=lb[i];
 const dt=new Date(d0+'T12:00:00');hover(el('rect',{x:x0,y:T,width:gw,height:H-B-T,fill:'transparent'},s),`<b>${lb[i]} ${dt.getDate()}/${dt.getMonth()+1}</b><br>${fmt(a)} · semana anterior ${fmt(b)}`)});
el('line',{x1:L,x2:W,y1:H-B,y2:H-B,stroke:'var(--axis)'},s);return H});
chart('chRank',(s,W,n)=>{const rows=D.rank,rh=n?40:30,L=n?0:Math.min(200,W*.28),pM=Math.max(0,...rows.map(r=>r[1])),nM=Math.max(0,...rows.map(r=>-r[1])),pr=pM>0?(n?96:150):6,pl=nM>0?(n?96:150):6,sc=(W-L-pr-pl)/((pM+nM)||1),mid=L+pl+nM*sc,x=v=>mid+v*sc;
el('line',{x1:mid,x2:mid,y1:0,y2:rows.length*rh,stroke:'var(--axis)'},s);
rows.forEach(([nm,dv,pc],i)=>{const yy=i*rh,by=n?yy+18:yy+7,up=dv>=0,xv=x(dv);
 if(n)el('text',{x:0,y:yy+13,style:'fill:var(--ink);font-weight:600;font-size:12px',class:'halo'},s).textContent=nm;else el('text',{x:L-10,y:yy+19,'text-anchor':'end',style:'fill:var(--ink);font-size:12px'},s).textContent=nm;
 el('rect',{x:Math.min(mid,xv),y:by,width:Math.max(2,Math.abs(xv-mid)),height:n?13:16,rx:3,fill:up?'var(--good)':'var(--crit)'},s);
 el('text',{x:up?xv+6:xv-6,y:by+(n?11:12),'text-anchor':up?'start':'end',style:up?'fill:var(--goodtxt);font-weight:600':'fill:var(--crit);font-weight:600'},s).textContent=(up?'+':'−')+kk(Math.abs(dv)).replace('R$ ','R$ ')+(n?'':(pc===null?' novo':' ('+(up?'+':'−')+br(Math.abs(pc))+'%)'));
 hover(el('rect',{x:0,y:yy,width:W,height:rh,fill:'transparent'},s),`<b>${nm}</b><br>${up?'+':'−'}${fmt(Math.abs(dv))} vs semana anterior`)});return rows.length*rh+4});
chart('chHeat',(s,W,n)=>{const lb=['Seg','Ter','Qua','Qui','Sex','Sáb','Dom'],L=34,T=4,cw=(W-L)/24,ch=n?20:24,max=Math.max(...D.heat.map(h=>h[2]))||1;
D.heat.forEach(([dw,h,v])=>{const r=(dw+6)%7,a=v/max;el('rect',{x:L+h*cw+1,y:T+r*ch+1,width:cw-2,height:ch-2,rx:3,fill:a<.02?'var(--grid)':`rgba(194,83,42,${(.12+.88*a).toFixed(2)})`},s);hover(el('rect',{x:L+h*cw,y:T+r*ch,width:cw,height:ch,fill:'transparent'},s),`<b>${lb[r]} ${h}h</b><br>média ${fmt(v)} por ${lb[r].toLowerCase()}`)});
lb.forEach((t,i)=>el('text',{x:L-6,y:T+i*ch+ch/2+4,'text-anchor':'end',style:'fill:var(--ink2);font-weight:600'},s).textContent=t);
for(let h=0;h<24;h+=n?6:3)el('text',{x:L+h*cw+cw/2,y:T+7*ch+14,'text-anchor':'middle'},s).textContent=h+'h';return T+7*ch+20});

}
