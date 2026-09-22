#!/usr/bin/env python3
"""Relatório semanal PGDash — gerador. Uso: python3 gen_semanal.py entrada.json saida.html
Lê o JSON descrito no SKILL.md (seção semanal) e monta a página. Blocos sem dados somem."""
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
def var(a,b): return (a/b-1)*100 if b else None
def dl(a,b,txt='vs semana anterior',inv=False,pp=False):
    if b in (None,0): return ''
    v=(a-b) if pp else var(a,b)
    good=(v<0) if inv else (v>0)
    s=('▲ ' if v>0 else '▼ ')+(br(abs(v),1)+' pp' if pp else br(abs(v))+'%')
    return f'<span class="{"up" if good else "down"}">{s}</span> {txt}'
def ds(s): y,m,d=s.split('-');return f'{d}/{m}'
import re as _re
def _txt(h,n=240):
    t=_re.sub(r'<[^>]+>','',h or '').replace('&nbsp;',' ').strip()
    t=_re.sub(r'\s+',' ',t)
    return t[:n]
def _acao(h): 
    t=_txt(h,160);return t.split('.')[0].strip()+'.' if '.' in t else t

DOW=['segunda','terça','quarta','quinta','sexta','sábado','domingo'];DOWc=[x.capitalize() for x in DOW]
MES=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
a0=dt.date.fromisoformat(D['semana_ini']);a1=dt.date.fromisoformat(D['semana_fim'])
hoje=dt.date.fromisoformat(D['hoje']) if D.get('hoje') else a1+dt.timedelta(days=1)
per=(f"{a0.day} a {a1.day} de {MES[a1.month-1]}" if a0.month==a1.month else f"{a0.day} de {MES[a0.month-1]} a {a1.day} de {MES[a1.month-1]}")+f" de {a1.year}"
S=D['sem'];A=D['ant'];T=D['textos'];BE=D.get('breakeven_roas',8.5)
# séries semanais a partir dos 56 dias
s56=D['serie56'];w8=[[s56[i][0],sum(x[1] for x in s56[i:i+7])] for i in range(0,len(s56),7)]
w8=[w for w in w8 if w[1] is not None][-8:]
prev4=[w[1] for w in w8[-5:-1]];m4=sum(prev4)/len(prev4) if prev4 else 0
best=max(w8[:-1],key=lambda w:w[1]) if len(w8)>2 else None
if best and best[0]==w8[-2][0]: best=None
dias=[[s56[-7+i][0],s56[-7+i][1],s56[-14+i][1]] for i in range(7)]
sec=[]
hdr=f'<header><h1>Relatório semanal <span class="acct">· {D["conta"]}</span></h1><div class="hdate">Semana de {per}</div><div class="sub">Dados capturados {D["capturado"]}</div></header>'
sec.append('<section class="card resumo"><h2>Resumo da semana</h2>'+''.join(f'<p>{x}</p>' for x in T['resumo'])+'</section>')
# Resultado
mp=lambda X:(X['mpre']-X['ads'])/X['fat']*100 if X['fat'] else 0
tc=lambda X:X['ads']/X['fat']*100 if X['fat'] else 0
tiles=f'''<div class="tiles">
 <div class="tile"><div class="lbl">Faturamento</div><div class="val">{k(S["fat"])}</div><div class="d">{dl(S["fat"],A["fat"])}</div><div class="d">{br(S["ped"])} pedidos · ticket {rs(S["ticket"],2)}</div></div>
 <div class="tile"><div class="lbl">Margem pós-Ads</div><div class="val">{br(mp(S),1)}%</div><div class="d">{dl(mp(S),mp(A),pp=True)}</div><div class="d">{k(S["mpre"]-S["ads"])} · pré-Ads {br(S["mpre"]/S["fat"]*100,1)}%</div></div>
 <div class="tile hero"><div class="lbl">TACOS</div><div class="val">{br(tc(S),1)}%</div><div class="d">{dl(tc(S),tc(A),inv=True,pp=True)}</div><div class="d">Ads {k(S["ads"])}</div></div>
 <div class="tile"><div class="lbl">Conversão</div><div class="val">{br(S["conv"],1)}%</div><div class="d">{dl(S["conv"],A["conv"],pp=True)}</div><div class="d">{br(S["vis"])} visitas ({pct(var(S["vis"],A["vis"])) if A.get("vis") else ""})</div></div></div>'''
L3=T.get('comp_leituras',['','',''])
comp=[[S['fat'],'Esta semana','var(--crit)',-1],[A['fat'],'Semana anterior','var(--ink2)',1],[m4,'Média 4 semanas','var(--acc)',-1]]
if best: comp.append([best[1],'Melhor das 8','var(--ink2)',1])
def crow(lbl,val,lei):
    v=var(S['fat'],val);return f'<tr><td>{lbl}<span class="lm">{lei}</span></td><td class="c">{k(val)}</td><td class="c {cls(v)}">{pct(v)}</td><td class="l lc small muted">{lei}</td></tr>'
bw=dt.date.fromisoformat(best[0]) if best else None
rows=crow(f'Semana anterior ({ds(D["serie56"][-14][0])} a {ds(D["serie56"][-8][0])})',A['fat'],L3[0])+crow('Média das 4 semanas anteriores',m4,L3[1])+(crow(f'Melhor semana das 8 (início {bw.day}/{bw.month})',best[1],L3[2]) if best else '')
canc=f' Cancelados na semana: {rs(S["canc"])} em {S.get("canc_ped",0)} pedidos (já fora do faturamento).' if S.get('canc') else ''
sec.append(f'''<section class="card"><h2>Resultado da semana</h2>{tiles}
 <div class="sect-title">Comparativo</div><div class="sect-desc">Faturamento da semana contra três referências.{canc}</div>
 <svg id="chComp" style="margin-bottom:14px"></svg>
 <div class="tscroll"><table class="tbl comp"><thead><tr><th>Referência</th><th class="c">Valor</th><th class="c">Semana vs referência</th><th class="l lc">Leitura</th></tr></thead><tbody>{rows}</tbody></table></div>
 <div class="sect-title">Últimas 8 semanas</div><div class="sect-desc">Faturamento por semana (segunda a domingo). A linha tracejada é a média das 4 semanas anteriores.</div>
 <svg id="chW8"></svg>
 <div class="sect-title">Dia a dia</div><div class="sect-desc">Faturamento em R$ mil. <span class="lg"><i style="background:var(--acc)"></i>esta semana</span> <span class="lg"><i style="background:var(--axis)"></i>semana anterior</span></div>
 <svg id="chDow"></svg></section>''')
# Produtos
prod=D.get('prod') or []
if prod:
    allr=[[n,f-fa,var(f,fa) if fa else None] for n,f,fa,u,mc in prod]
    dn=sorted([r for r in allr if r[1]<0],key=lambda r:r[1])[:3];up=sorted([r for r in allr if r[1]>0],key=lambda r:-r[1])[:8-len(dn)]
    rk=up+sorted(dn,key=lambda r:-r[1])
    trs=''
    for n,f,fa,u,mc in sorted(prod,key=lambda p:-p[1])[:10]:
        v=var(f,fa) if fa else None;m=mc/f*100 if f else 0
        vv='<span class="chip new">novo</span>' if v is None else f'<span class="{cls(v)}">{pct(v)}</span>'
        trs+=f'<tr><td><b>{n}</b></td><td class="c">{rs(f)}</td><td class="c">{vv}</td><td class="c">{br(u)}</td><td class="c"><span class="{"down" if m<5 else ""}">{br(m,1)}%</span></td></tr>'
    sec.append(f'''<section class="card"><h2>Quem subiu e quem caiu</h2>
 <div class="sect-desc">Variação do faturamento de cada produto contra a semana anterior, em R$. Até 8 produtos: os que mais subiram e os que mais caíram.</div>
 <svg id="chRank"></svg>
 <div class="tscroll" style="margin-top:14px"><table class="tbl"><thead><tr><th>Produto</th><th class="c">Faturamento</th><th class="c">vs anterior</th><th class="c">Unidades</th><th class="c">Margem</th></tr></thead><tbody>{trs}</tbody></table></div>
 <p class="small muted" style="margin:8px 0 0">Margem de contribuição antes dos Ads, direto da DRE. Em vermelho, abaixo de 5%.</p></section>''')
# Ads
ad=D.get('ads');camp=D.get('camp') or []
if ad:
    aa=ad.get('ant',{})
    at=f'''<div class="tiles">
 <div class="tile"><div class="lbl">Investimento</div><div class="val">{k(ad["custo"])}</div><div class="d">{dl(ad["custo"],aa.get("custo"),inv=False).replace('class="up"','class="neu"').replace('class="down"','class="neu"')}</div></div>
 <div class="tile"><div class="lbl">ROAS</div><div class="val">{br(ad["roas"],1)}×</div><div class="d">{dl(ad["roas"],aa.get("roas"))}</div></div>
 <div class="tile hero"><div class="lbl">TACOS</div><div class="val">{br(ad["tacos"],1)}%</div><div class="d">{dl(ad["tacos"],aa.get("tacos"),inv=True,pp=True)}</div></div>
 <div class="tile"><div class="lbl">CTR</div><div class="val">{br(ad["ctr"],2)}%</div><div class="d">{br(ad["cl"])} cliques · CPC {rs(ad["cpc"],2)}</div></div></div>'''
    rows=''
    for n,imp,cl,ctr,cpc,cu,re,ro in camp:
        h=('crit','Alerta') if (ro is None or ro<BE*0.6) else ('warn','Atenção') if ro<BE else ('ok','Saudável')
        sh=cu/ad['custo']*100 if ad['custo'] else 0
        rows+=f'<tr><td><b>{n}</b></td><td class="c">{br(imp)}</td><td class="c">{br(cl)}</td><td class="c">{br(ctr,1)}%</td><td class="c">{rs(cpc,2)}</td><td class="c">{rs(cu)} <span class="muted">({br(sh)}%)</span></td><td class="c">{rs(re) if re else "<span class=down>—</span>"}</td><td class="c">{br(ro,1)+"×" if ro else "<span class=down>—</span>"}</td><td class="c"><span class="chip {h[0]}">{h[1]}</span></td></tr>'
    ct=f'''<div class="tscroll" style="margin-top:14px"><table class="tbl"><thead><tr><th>Campanha</th><th class="c">Impressões</th><th class="c">Cliques</th><th class="c">CTR</th><th class="c">CPC</th><th class="c">Custo (% do total)</th><th class="c">Receita</th><th class="c">ROAS</th><th class="c">Saúde</th></tr></thead><tbody>{rows}</tbody></table></div>''' if camp else ''
    sec.append(f'''<section class="card"><h2>Anúncios da semana</h2>{at}
 <div class="sect-desc" style="margin-top:12px">{len(camp)} campanhas com atividade · saúde pelo ROAS da semana contra o ponto de equilíbrio da conta ({br(BE,1)}).</div>{ct}
 {"<p class='small muted' style='margin:8px 0 0'>"+T["camp_nota"]+"</p>" if T.get("camp_nota") else ""}</section>''')
# Heatmap
heat=D.get('heat') or []
if heat:
    bd=D.get('heat_leitura','')
    sec.append(f'''<section class="card"><h2>Quando a conta vende</h2>
 <div class="sect-desc">Faturamento médio por dia da semana e hora, nas últimas 4 semanas ({ds(D["heat_de"])} a {ds(D["heat_ate"])}). Quanto mais escuro, mais venda.</div>
 <svg id="chHeat"></svg>{"<p class='small muted' style='margin:8px 0 0'>"+bd+"</p>" if bd else ""}</section>''')
# Plano de compra
rep=D.get('repor') or [];pr=D['params'];r=D.get('rup') or {'n':0}
if rep:
    ag=[x for x in rep if x[1]=='REPOR_AGORA'];eb=[x for x in rep if x[1]!='REPOR_AGORA']
    cap=lambda L:sum(x[6] or 0 for x in L)
    rows=''
    for n,st,e,tr,trc,q,cp,ca,at in rep:
        chip='<span class="chip crit">agora</span>' if st=='REPOR_AGORA' else '<span class="chip warn">em breve</span>'
        quando=f'<span class="down">venceu há {at} d</span>' if at else ds(ca) if ca else '—'
        trtxt=f'{tr} <span class="muted">({br(trc,0)}d)</span>' if tr else '<span class="muted">—</span>'
        rows+=f'<tr><td><b>{n}</b></td><td class="c">{chip}</td><td>{e}</td><td>{trtxt}</td><td class="c">{q}</td></tr>'
    perda=f'<div class="tile"><div class="lbl">Venda perdida hoje</div><div class="val down">{k(r["perda"])}/dia</div><div class="d">{r["n"]} produtos zerados</div></div>' if r.get('n') else f'<div class="tile"><div class="lbl">Venda perdida hoje</div><div class="val">R$ 0</div><div class="d">nenhum produto zerado</div></div>'
    sec.append(f'''<section class="card"><h2>Plano de abastecimento</h2>
 <div class="tiles t3">
  <div class="tile"><div class="lbl">Comprar agora</div><div class="val down">{k(cap(ag))}</div><div class="d">{len(ag)} produtos · {br(sum(x[5] for x in ag))} un.</div></div>
  <div class="tile"><div class="lbl">Comprar em breve</div><div class="val">{k(cap(eb))}</div><div class="d">{len(eb)} produtos · {br(sum(x[5] for x in eb))} un.</div></div>
  {perda}</div>
 <div class="tscroll" style="margin-top:14px"><table class="tbl"><thead><tr><th>Produto</th><th class="c">Prioridade</th><th>Estoque</th><th>Trânsito</th><th class="c">Sugestão</th></tr></thead><tbody>{rows}</tbody></table></div>
 <p class="small muted" style="margin:8px 0 0">Estoque de hoje. Sugestão e capital são do PGDash, com prazo de {pr["lt"]} dias + {pr["seg"]} de segurança e cobertura-alvo de {pr["alvo"]} dias; já descontam o trânsito. Total: <b class="b">{rs(cap(rep))}</b>.</p></section>''')
# Projeção
p=D.get('proj')
if p:
    meta=p.get('meta');mref=dt.date.fromisoformat(D['semana_fim'])
    if meta:
        falta=meta-p['mtd'];t1=f'{br(p["pct_meta"])}% da meta · {p["dec"]} de {p["dec"]+p["rest"]} dias';t2=f'{br(p["c3"]/meta*100)}% da meta · ritmo de 7 dias'
        ptxt=(f'Faltam <b class="b">{k(falta)}</b> para a meta de {k(meta)}: <b class="b">{rs(p["ritmo"])}/dia</b> nos {p["rest"]} dias restantes.') if falta>0 else f'<b class="b">Meta de {k(meta)} já batida.</b>'
    else: t1=f'{p["dec"]} de {p["dec"]+p["rest"]} dias';t2='ritmo dos últimos 7 dias';ptxt='Meta do mês não cadastrada no PGDash.'
    if p.get('sem_rup') and p['sem_rup']>p['c3']+1: ptxt+=f' Com estoque, o mês fecharia em <b class="b">{k(p["sem_rup"])}</b>.'
    sec.append(f'''<section class="card"><h2>Projeção de {MES[mref.month-1]}</h2>
 <div class="tiles" style="grid-template-columns:1fr 1fr">
  <div class="tile"><div class="lbl">Acumulado até {ds(D["semana_fim"])}</div><div class="val" style="font-size:20px">{k(p["mtd"])}</div><div class="d">{t1}</div></div>
  <div class="tile"><div class="lbl">Fechamento previsto</div><div class="val" style="font-size:20px">{k(p["c3"])}</div><div class="d">{t2}</div></div></div>
 <svg id="chProj" style="margin-top:12px"></svg><p class="small muted" style="margin:4px 0 0">{ptxt}</p></section>''')
# Calendário e clima (igual ao diário)
ev=D.get('eventos') or [];wx=D.get('clima')
if ev or wx:
    cards=''
    for e in ev:
        its=''.join(f'<div class="sk"><span class="nm">{a}</span>'+(f'<span class="chip {b}">{c}</span>' if b else f'<span class="b">{c}</span>')+'</div>' for a,b,c in e['itens'])
        dd=dt.date.fromisoformat(e['data']);dias_=(dd-hoje).days
        cards+=f'<div class="evc"><div class="bar {e.get("cor","info")}"></div><div class="body"><div class="top"><div><div class="name">{e["nome"]}</div><div class="when">{DOWc[dd.weekday()]}, {dd.day} de {MES[dd.month-1]}</div></div><div class="cd"><b>{dias_}</b><span>dias</span></div></div><div class="skus">{its}</div><div class="foot">{e.get("rodape","")}</div></div></div>'
    wxh=''
    if wx:
        wxh=f'''<div class="wx"><div class="hd"><div><div class="name">{ {"frio":"Frio","calor":"Calor"}.get(wx.get("tipo"),"Chuva") } em {wx["cidade"]} · próximos 7 dias</div><div class="small muted">{wx.get("afeta","")}</div></div></div>
   {"<div class='wxalert'>⚠ "+wx["alerta"]+"</div>" if wx.get("alerta") else ""}<div class="wxrow" id="wx"></div>
   <div class="small muted" style="margin-top:8px">{wx.get("nota","")} Fonte: AccuWeather{" e INMET" if wx.get("alerta") else ""}, consultados {D["capturado"].split(" às")[0]}.</div></div>'''
    sec.append(f'''<section class="card"><h2>Próximas semanas</h2>
 {('<div class="sect-desc">Próximas 10 semanas. Só aparecem datas ligadas a produtos desta conta; os triângulos marcam a data-limite de compra.</div><svg id="chCal"></svg>') if ev else ''}
 <div class="cal">{cards}{wxh}</div></section>''')
# SEO
seo=[x for x in (D.get('seo') or []) if x[3]]
if seo:
    seo.sort(key=lambda x:x[3])
    rows=''.join(f'<tr><td><b>{kw}</b></td><td class="l">{an or "—"}</td><td class="c">{pos}º</td><td class="c {"up" if v>0 else "down"}">{"▲" if v>0 else "▼"} {abs(v)}<span class="era"> (era {pos+v}º)</span></td></tr>' for kw,an,pos,v in seo)
    sec.append(f'<section class="card"><h2>Ranqueamento na semana</h2><div class="tscroll"><table class="tbl seo"><thead><tr><th>Palavra-chave</th><th class="l">Anúncio</th><th class="c">Posição</th><th class="c">Variação</th></tr></thead><tbody>{rows}</tbody></table></div><p class="small muted" style="margin:6px 0 0">Só as palavras que mudaram de posição. Quedas primeiro.</p></section>')
sec.append('<section class="card actions"><h2>Decisões da semana</h2><ol>'+''.join(f'<li>{a}</li>' for a in T['acoes'])+'</ol></section>')
sy=D.get('sync',{})
foot=f'<footer><span>Fonte: PGDash{" · AccuWeather" if wx else ""}{" · INMET" if wx and wx.get("alerta") else ""}</span><span>Vendas sincronizadas há {sy.get("vendas","?")} min · estoque há {sy.get("estoque","?")} min · Ads há {sy.get("ads","?")} min</span></footer>'

# memória: resumo compacto da semana, lido pela próxima rodada
_sub=sorted([x for x in prod if (x[2] or 0)>0 and x[1]>x[2]],key=lambda x:-(x[1]-x[2]))[:3]
_cai=sorted([x for x in prod if (x[2] or 0)>0 and x[1]<x[2]],key=lambda x:(x[1]-x[2]))[:3]
MEM=dict(fat=S['fat'],ped=S.get('ped'),ticket=S.get('ticket'),mpre=S.get('mpre'),ads=S.get('ads'),
 conv=S.get('conv'),vis=S.get('vis'),fat_ant=A.get('fat'),
 roas=(ad or {}).get('roas'),tacos=(ad or {}).get('tacos'),
 subiu=[x[0] for x in _sub],caiu=[x[0] for x in _cai],
 camp_ruins=[c[0] for c in camp if c[5]>0 and (c[7] is None or c[7]<BE)][:6],
 repor=[x[0] for x in rep][:8],rup_n=r.get('n',0),perda=r.get('perda'),
 acoes=[_acao(a) for a in T.get('acoes',[])],
 risco=_txt(T['resumo'][2]) if len(T.get('resumo',[]))>2 else None,
 clima=(wx or {}).get('tipo'))
inner=hdr+''.join(sec)+foot
body='<div id="tip"></div><div class="wrap"><nav class="hist" id="hist" hidden></nav><div id="rel">'+inner+'</div></div>'
J=dict(projHoje=f'até {a1.day}/{a1.month}',comp=comp,compBig='Esta semana',w8=w8,m4=m4,dias=dias,rank=rk if prod else [],heat=heat,
 proj=[p['mtd']/1000,p['c3']/1000,(p.get('sem_rup') or p['c3'])/1000,(p.get('meta') or 0)/1000] if p else [0,0,0,0],
 wx=(wx or {}).get('dias',[]),wxt=(wx or {}).get('tipo','chuva'),hoje=hoje.isoformat(),
 ev=[[e['data'],e['nome'],e.get('comprar_ate'),'var(--crit)' if e.get('cor')=='crit' else 'var(--line)'] for e in ev],estacao=D.get('estacao'),
 serie=[],marcos=[],lost=[],ctr=[],ws=[],wd=0,lt=pr['lt']+pr['seg'])
js=open(os.path.join(H,'charts.js')).read()+'\n'+open(os.path.join(H,'charts_sem.js')).read()+'\ndrawAll();drawSem();'
ED=dict(tipo='semanal',data=D['semana_fim'],rotulo=f"{a0.day:02d}/{a0.month:02d} a {a1.day:02d}/{a1.month:02d}",fat=S['fat'])
hist=open(os.path.join(H,'hist.js')).read()
out=f'<title>Relatório semanal {D["conta"]}</title><meta name="color-scheme" content="light only"><style>{css}</style>{body}<script>{cj}\nvar D={json.dumps(J,ensure_ascii=False)};\nvar ED={json.dumps(ED,ensure_ascii=False)};\nconst REL0=document.getElementById("rel").innerHTML;\n{js}\n{hist}</script>'
open(OUT,'w').write(out)
od=os.path.dirname(os.path.abspath(OUT))
json.dump(dict(data=ED['data'],rotulo=ED['rotulo'],fat=ED['fat'],body=inner,D=J),open(os.path.join(od,'edicao.json'),'w'),ensure_ascii=False)
json.dump(dict(data=ED['data'],rotulo=ED['rotulo'],fat=ED['fat'],mem=MEM),open(os.path.join(od,'indice.json'),'w'),ensure_ascii=False)
print('ok',OUT,'| edicao.json e indice.json em',od)
