#!/usr/bin/env python3
"""Relatório diário PGDash — gerador. Uso: python3 gen_diario.py entrada.json saida.html
Lê o JSON compacto descrito no SKILL.md e monta a página. Blocos sem dados somem."""
import json,sys,os,datetime as dt
H=os.path.dirname(os.path.abspath(__file__))
D=json.load(open(sys.argv[1]));OUT=sys.argv[2]
css=open(os.path.join(H,'style.css')).read();cj=open(os.path.join(H,'common.js')).read()
def br(v,d=0): return f"{v:,.{d}f}".replace(',','X').replace('.',',').replace('X','.')
def rs(v,d=0): return 'R$ '+br(v,d)
def k(v):
    s=br(v/1000,1);return 'R$ '+(s[:-2] if s.endswith(',0') else s)+' mil'
def pct(v): return ('▲ ' if v>0 else '▼ ')+br(abs(v))+'%'
def cls(v): return 'up' if v>0 else 'down'
def ds(s): y,m,d=s.split('-');return f'{d}/{m}'
DOW=['segunda','terça','quarta','quinta','sexta','sábado','domingo'];DOWc=[x.capitalize() for x in DOW]
MES=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
d=dt.date.fromisoformat(D['data']);wd=d.weekday();dowp=DOW[wd]+'s'
title=f"{DOWc[wd]}, {d.day} de {MES[d.month-1]} de {d.year}"
hoje=d+dt.timedelta(days=1)
dia=D['dia'];f=D['funil'];p=D['proj'];r=D.get('rup') or {'n':0};pr=D['params'];T=D['textos']
serie=D['serie'];d1=serie[-2][1];d7=serie[-8][1];m7=sum(x[1] for x in serie[-8:-1])/7
camp=D.get('camp') or [];skus=D.get('skus') or []
roas=(sum(c[6] for c in camp)/dia['ads']) if dia['ads'] else 0
BE=D.get('breakeven_roas',8.5)
zer=[s for s in skus if s[1]==0 or s[5]<1];withstock=[s for s in skus if s[5]>=1]
lost=[[s[0],s[9],s[2],s[10]] for s in skus if s[9]]
L4=T.get('comp_leituras',['','','',''])
sec=[]
# Cabeçalho + resumo
hdr=f'<header><h1>Relatório diário <span class="acct">· {D["conta"]}</span></h1><div class="hdate">{title}</div><div class="sub">Dados capturados {D["capturado"]}</div></header>'
sec.append('<section class="card resumo"><h2>Resumo</h2>'+''.join(f'<p>{x}</p>' for x in T['resumo'])+'</section>')
# Resultado do dia
margp=dia['mpos']/dia['fat']*100 if dia['fat'] else 0
tiles=f'''<div class="tiles">
 <div class="tile"><div class="lbl">Faturamento</div><div class="val">{rs(dia["fat"])}</div><div class="d">{dia["ped"]} pedidos · ticket {rs(dia["ticket"])}</div></div>
 <div class="tile"><div class="lbl">Margem pós-Ads</div><div class="val">{br(margp,1)}%</div><div class="d">{rs(dia["mpos"])} · pré-Ads {br(dia["mpre"]/dia["fat"]*100 if dia["fat"] else 0,1)}%</div></div>
 <div class="tile hero"><div class="lbl">TACOS</div><div class="val">{br(dia["ads"]/dia["fat"]*100 if dia["fat"] else 0,1)}%</div><div class="d">Ads {rs(dia["ads"])} · ROAS {br(roas,1)}×</div></div>
 <div class="tile"><div class="lbl">Conversão</div><div class="val">{br(f["conv"],1)}%</div><div class="d">{br(f["vis"])} visitas · {dia["un"]} unidades</div></div></div>'''
comp=[[dia['fat'],'Ontem','var(--crit)',-1],[d1,'Dia anterior','var(--ink2)',1],[dia['mediana'],f'Mediana 4 {dowp}','var(--acc)',-1],[m7,'Média 7 dias','var(--ink2)',1],[d7,f'{DOWc[wd]} anterior','var(--ink2)',-1]]
def crow(lbl,val,vs,lei): return f'<tr><td>{lbl}<span class="lm">{lei}</span></td><td class="c">{rs(val)}</td><td class="c {cls(vs)}">{pct(vs)}</td><td class="l lc small muted">{lei}</td></tr>'
atip='<span class="chip warn">dia atípico</span>' if dia.get('d7_atip') else '<span class="small muted">'+L4[3]+'</span>'
comp_rows=crow(f'Dia anterior ({DOW[(wd-1)%7][:3]} {ds(serie[-2][0])})',d1,dia['vs_d1'],L4[0])+crow(f'Mediana 4 {dowp}',dia['mediana'],dia['vs_med'],L4[1])+crow('Média 7 dias',m7,dia['vs_m7'],L4[2])+ \
 f'<tr><td>{DOWc[wd]} anterior ({ds(serie[-8][0])})<span class="lm">{atip}</span></td><td class="c">{rs(d7)}</td><td class="c {cls(dia["vs_d7"])}">{pct(dia["vs_d7"])}</td><td class="l lc">{atip}</td></tr>'
sec.append(f'''<section class="card"><h2>Resultado do dia</h2>{tiles}
 <div class="sect-title">Comparativo</div><div class="sect-desc">Ontem contra quatro referências.{" A "+DOW[wd]+" anterior foi atípica e não serve como dia normal." if dia.get("d7_atip") else ""}</div>
 <svg id="chComp" viewBox="0 0 840 132" style="margin-bottom:14px"></svg>
 <div class="tscroll"><table class="tbl comp"><thead><tr><th>Referência</th><th class="c">Valor</th><th class="c">Ontem vs referência</th><th class="l lc">Leitura</th></tr></thead><tbody>{comp_rows}</tbody></table></div>
 <div class="sect-title">Últimos 28 dias</div><div class="sect-desc">Faturamento diário em R$ mil. {DOWc[wd]}s em cor cheia; a linha azul é a média móvel de 7 dias.</div>
 <svg id="chRev" viewBox="0 0 840 190"></svg></section>''')
# Venda perdida
if r.get('n',0)>0 and lost:
    ult=dt.date(d.year,d.month,1).replace(day=28)+dt.timedelta(days=4);ult=ult-dt.timedelta(days=ult.day)
    sec.append(f'''<section class="card"><h2>Venda perdida por falta de estoque</h2>
 <div class="tiles t3">
  <div class="tile"><div class="lbl">Perdido por dia</div><div class="val down">{k(r["perda"])}</div><div class="d">{r["n"]} produtos zerados</div></div>
  <div class="tile"><div class="lbl">Até {ult.strftime("%d/%m")}</div><div class="val down">≈ {k(r["perda_mes"])}</div><div class="d">{p["rest"]} dias × {k(r["perda"])}</div></div>
  <div class="tile"><div class="lbl">Próximo a zerar</div><div class="val nm">{r.get("prox","—")}</div><div class="d">{r.get("prox_tr",0)} un. a caminho</div></div></div>
 <svg id="chLost" viewBox="0 0 840 {len(lost)*32+8}" style="margin-top:14px"></svg>
 <p class="small muted" style="margin:6px 0 0">Cálculo do PGDash: venda média por dia × preço médio dos últimos 14 dias. Entre parênteses, o que já está em trânsito.</p></section>''')
# Tráfego + projeção
ctr14=D['ctr14'];ctr_avg=sum(x[1] for x in ctr14)/max(1,sum(x[2] for x in ctr14))*100
meta=p.get('meta')
if meta:
    t1=f'{br(p["pct_meta"])}% da meta · {p["dec"]} de {p["dec"]+p["rest"]} dias';t2=f'{br(p["c3"]/meta*100)}% da meta · ritmo de 3 dias'
    falta=meta-p['mtd']
    ptxt=(f'Faltam <b class="b">{k(falta)}</b> para a meta de {k(meta)}: <b class="b">{rs(p["ritmo"])}/dia</b> nos {p["rest"]} dias restantes' + (f', abaixo do ritmo atual ({k(p["m3"])}/dia).' if p["ritmo"]<p["m3"] else f', acima do ritmo atual ({k(p["m3"])}/dia).')) if falta>0 else f'<b class="b">Meta de {k(meta)} já batida.</b>'
else:
    t1=f'{p["dec"]} de {p["dec"]+p["rest"]} dias';t2='ritmo dos últimos 3 dias';ptxt='Meta do mês não cadastrada no PGDash.'
if p.get('sem_rup') and p['sem_rup']>p['c3']+1: ptxt+=f' Com estoque, o mês fecharia em <b class="b">{k(p["sem_rup"])}</b>.'
sec.append(f'''<div class="row2">
<section class="card"><h2>Tráfego e anúncios</h2>
 <div class="tiles t3">
  <div class="tile"><div class="lbl">Impressões</div><div class="val" style="font-size:20px">{br(f["imp"]/1000)} mil</div><div class="d">Ads</div></div>
  <div class="tile"><div class="lbl">Cliques</div><div class="val" style="font-size:20px">{f["cl"]}</div><div class="d">CPC {rs(dia["ads"]/f["cl"],2) if f["cl"] else "—"}</div></div>
  <div class="tile"><div class="lbl">CTR</div><div class="val" style="font-size:20px">{br(f["ctr"],2)}%</div><div class="d">média 14 dias {br(ctr_avg,2)}%</div></div></div>
 <svg id="chCtr" viewBox="0 0 400 120" style="margin-top:12px"></svg></section>
<section class="card"><h2>Projeção de {MES[d.month-1]}</h2>
 <div class="tiles" style="grid-template-columns:1fr 1fr">
  <div class="tile"><div class="lbl">Acumulado</div><div class="val" style="font-size:20px">{k(p["mtd"])}</div><div class="d">{t1}</div></div>
  <div class="tile"><div class="lbl">Fechamento previsto</div><div class="val" style="font-size:20px">{k(p["c3"])}</div><div class="d">{t2}</div></div></div>
 <svg id="chProj" viewBox="0 0 400 70" style="margin-top:12px"></svg>
 <p class="small muted" style="margin:4px 0 0">{ptxt}</p></section></div>''')
# Campanhas
if camp:
    rows=''
    for n,imp,cl,ctr,cpc,cu,re,ro in camp:
        h=('crit','Alerta') if (ro is None or ro<BE*0.6) else ('warn','Atenção') if ro<BE else ('ok','Saudável')
        rows+=f'<tr><td><b>{n}</b></td><td class="c">{br(imp)}</td><td class="c">{cl}</td><td class="c">{br(ctr,1)}%</td><td class="c">{rs(cpc,2)}</td><td class="c">{rs(cu,2)}</td><td class="c">{rs(re,2) if re else "<span class=down>—</span>"}</td><td class="c">{br(ro,1)+"×" if ro else "<span class=down>—</span>"}</td><td class="c"><span class="chip {h[0]}">{h[1]}</span></td></tr>'
    sec.append(f'''<section class="card"><h2>Anúncios por campanha</h2>
 <div class="sect-desc">Ontem, {len(camp)} campanhas com atividade · custo total {rs(dia["ads"])} · saúde pelo ROAS contra o ponto de equilíbrio da conta ({br(BE,1)}).</div>
 <div class="tscroll"><table class="tbl"><thead><tr><th>Campanha</th><th class="c">Impressões</th><th class="c">Cliques</th><th class="c">CTR</th><th class="c">CPC</th><th class="c">Custo</th><th class="c">Receita</th><th class="c">ROAS</th><th class="c">Saúde</th></tr></thead><tbody>{rows}</tbody></table></div>
 {"<p class='small muted' style='margin:8px 0 0'>"+T["camp_nota"]+"</p>" if T.get("camp_nota") else ""}</section>''')
# Estoque
if skus:
    zc=''
    for z in zer:
        lvl='ok' if z[10]>=pr['lt'] else 'warn' if z[10]>=2 else 'crit'
        zc+=f'<div class="zc {lvl}"><div class="zn">{z[0]}</div><div class="zr"><span class="ze">{z[1]} un. em estoque</span></div><span class="chip {lvl}">{z[2]} a caminho · cobre {br(z[10],0)} dia{"s" if round(z[10])!=1 else ""}</span></div>'
    rows=''
    for n,e,tr,m,t,cob,rup,sug,cap,perda,trc in skus:
        trtxt=f'{tr} <span class="muted">({br(trc,0)}d)</span>' if tr else '<span class="muted">—</span>'
        acaba='<span class="chip crit">zerado</span>' if e==0 else '<span class="chip crit">hoje</span>' if cob<1 else ds(rup)
        rows+=f'<tr><td><b>{n}</b></td><td>{e}</td><td>{trtxt}</td><td>{br(m,1)}</td><td><span class="{cls(t)}">{pct(t)}</span>{" <span class=muted>●</span>" if e<10 and t<0 else ""}</td><td>{acaba}</td><td class="c">{sug}</td><td>{rs(cap or 0)}</td></tr>'
    sec.append(f'''<section class="card"><h2>Estoque e reposição</h2>
 <div class="pstrip"><div class="ps"><span>Prazo de reposição</span><b>{pr["lt"]} dias</b></div><div class="op">+</div><div class="ps"><span>Segurança</span><b>{pr["seg"]} dias</b></div><div class="op">=</div><div class="ps tot"><span>Prazo total</span><b>{pr["lt"]+pr["seg"]} dias</b></div><div class="ps alvo"><span>Cobertura-alvo</span><b>{pr["alvo"]} dias</b></div></div>
 {('<div class="zhead"><span>Sem estoque agora</span><small>'+str(len(zer))+' produtos · verde: o trânsito cobre ao menos o prazo de reposição</small></div><div class="zgrid">'+zc+'</div>') if zer else ''}
 {('<div class="sect-desc" style="margin-top:14px">Dias de estoque dos produtos que ainda têm saldo, sem contar o trânsito. Na faixa vermelha, uma compra feita hoje não chega antes de acabar.</div><svg id="chCov" viewBox="0 0 840 '+str(len(withstock)*28+52)+'"></svg>') if withstock else ''}
 <div class="tscroll" style="margin-top:14px"><table class="tbl"><thead><tr><th>Produto</th><th>Estoque</th><th>Trânsito</th><th>Venda/dia</th><th>Tendência</th><th>Acaba em</th><th class="c">Sugestão</th><th>Capital</th></tr></thead><tbody>{rows}</tbody></table></div>
 <p class="small muted" style="margin:8px 0 0">Nos produtos zerados (●) a tendência cai por falta de produto, não de procura. Sugestão e capital são do PGDash e já descontam o trânsito: total <b class="b">{rs(D.get("cap_total",0))}</b>.</p></section>''')
# Calendário e clima
ev=D.get('eventos') or [];wx=D.get('clima')
if ev or wx:
    cards=''
    for e in ev:
        its=''.join(f'<div class="sk"><span class="nm">{a}</span>'+(f'<span class="chip {b}">{c}</span>' if b else f'<span class="b">{c}</span>')+'</div>' for a,b,c in e['itens'])
        dd=dt.date.fromisoformat(e['data']);dias=(dd-hoje).days
        cards+=f'<div class="evc"><div class="bar {e.get("cor","info")}"></div><div class="body"><div class="top"><div><div class="name">{e["nome"]}</div><div class="when">{DOWc[dd.weekday()]}, {dd.day} de {MES[dd.month-1]}</div></div><div class="cd"><b>{dias}</b><span>dias</span></div></div><div class="skus">{its}</div><div class="foot">{e.get("rodape","")}</div></div></div>'
    wxh=''
    if wx:
        wxh=f'''<div class="wx"><div class="hd"><div><div class="name">{ {"frio":"Frio","calor":"Calor"}.get(wx.get("tipo"),"Chuva") } em {wx["cidade"]} · próximos 7 dias</div><div class="small muted">{wx.get("afeta","")}</div></div></div>
   {"<div class='wxalert'>⚠ "+wx["alerta"]+"</div>" if wx.get("alerta") else ""}<div class="wxrow" id="wx"></div>
   <div class="small muted" style="margin-top:8px">{wx.get("nota","")} Fonte: AccuWeather{" e INMET" if wx.get("alerta") else ""}, consultados {D["capturado"].split(" às")[0]}.</div></div>'''
    sec.append(f'''<section class="card"><h2>Calendário e clima</h2>
 {('<div class="sect-desc">Próximas 10 semanas. Só aparecem datas ligadas a produtos desta conta; os triângulos marcam a data-limite de compra.</div><svg id="chCal" viewBox="0 0 840 110"></svg>') if ev else ''}
 <div class="cal">{cards}{wxh}</div></section>''')
# SEO
seo=D.get('seo') or []
if seo:
    rows=''.join(f'<tr><td><b>{kw}</b></td><td class="l">{an}</td><td class="c">{pos}º</td><td class="c down">▼ {abs(v)}<span class="era"> (era {was}º)</span></td></tr>' for kw,an,pos,v,was in seo[:3])
    sec.append(f'<section class="card"><h2>Queda no ranqueamento</h2><div class="tscroll"><table class="tbl seo"><thead><tr><th>Palavra-chave</th><th class="l">Anúncio</th><th class="c">Posição</th><th class="c">Variação</th></tr></thead><tbody>{rows}</tbody></table></div><p class="small muted" style="margin:6px 0 0">Este bloco só aparece quando alguma palavra cai.</p></section>')
sec.append('<section class="card actions"><h2>O que fazer hoje</h2><ol>'+''.join(f'<li>{a}</li>' for a in T['acoes'])+'</ol></section>')
sy=D.get('sync',{})
foot=f'<footer><span>Fonte: PGDash{" · AccuWeather" if wx else ""}{" · INMET" if wx and wx.get("alerta") else ""}</span><span>Vendas sincronizadas há {sy.get("vendas","?")} min · estoque há {sy.get("estoque","?")} min · Ads há {sy.get("ads","?")} min</span></footer>'
inner=hdr+''.join(sec)+foot
body='<div id="tip"></div><div class="wrap"><nav class="hist" id="hist" hidden></nav><div id="rel">'+inner+'</div></div>'
J=dict(serie=serie,comp=comp,lost=lost,ctr=ctr14,ws=[[s[0],s[1],s[5]] for s in withstock],proj=[p['mtd']/1000,p['c3']/1000,(p.get('sem_rup') or p['c3'])/1000,(meta or 0)/1000],
 wx=(wx or {}).get('dias',[]),wxt=(wx or {}).get('tipo','chuva'),wd=wd,lt=pr['lt']+pr['seg'],marcos=D.get('marcos',[]),hoje=hoje.isoformat(),
 ev=[[e['data'],e['nome'],e.get('comprar_ate'),'var(--crit)' if e.get('cor')=='crit' else 'var(--line)'] for e in ev],estacao=D.get('estacao'))
js=open(os.path.join(H,'charts.js')).read()+'\ndrawAll();'
ED=dict(tipo='diario',data=D['data'],rotulo=f"{DOW[wd][:3]} {d.day:02d}/{d.month:02d}",fat=dia['fat'])
hist=open(os.path.join(H,'hist.js')).read()
out=f'<title>Relatório diário {D["conta"]}</title><meta name="color-scheme" content="light only"><style>{css}</style>{body}<script>{cj}\nvar D={json.dumps(J,ensure_ascii=False)};\nvar ED={json.dumps(ED,ensure_ascii=False)};\nconst REL0=document.getElementById("rel").innerHTML;\n{js}\n{hist}</script>'
open(OUT,'w').write(out)
od=os.path.dirname(os.path.abspath(OUT))
json.dump(dict(data=ED['data'],rotulo=ED['rotulo'],fat=ED['fat'],body=inner,D=J),open(os.path.join(od,'edicao.json'),'w'),ensure_ascii=False)
json.dump(dict(data=ED['data'],rotulo=ED['rotulo'],fat=ED['fat']),open(os.path.join(od,'indice.json'),'w'),ensure_ascii=False)
print('ok',OUT,'| edicao.json e indice.json em',od)
