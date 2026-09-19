---
name: relatorio-semanal
description: Gera e publica o Relatório semanal (segunda a domingo) da conta do Mercado Livre a partir do PGDash. Use quando a tarefa agendada de segunda ou o cliente pedir o "relatório semanal" ou o "fechamento da semana".
---

# Relatório semanal PGDash

Fechamento da semana anterior (segunda a domingo) de uma conta do Mercado Livre, para profissionais de operação. Mesmo visual do Relatório diário. O visual e o cálculo já estão prontos no gerador anexado ao artefato do semanal: seu trabalho é **coletar, mapear para o JSON de entrada, escrever os textos, publicar e guardar no histórico**. Não recrie o HTML à mão.

Os parâmetros da conta (nome da conta, URL do artefato, `clima` = auto/sempre/nunca, cidade do clima com `locationKey`, ponto de equilíbrio de ROAS) vêm da tarefa agendada que chamou esta skill. Quando o cliente pedir o relatório fora da tarefa, procure a página dele com `Artifact` `action: "list"` (título "Relatório semanal <conta>") e use os parâmetros da tarefa agendada "Relatório semanal · <conta>" (`list_triggers`). Se não houver página, diga em uma frase que é preciso rodar "configurar relatórios" antes e pare.

Datas: `HOJE` = hoje em America/Sao_Paulo. `FIM` = o domingo mais recente antes de hoje. `INI` = FIM − 6 (a segunda). `ANT_INI`/`ANT_FIM` = a semana anterior (INI − 7, FIM − 7).

## Passo 1 — Baixar o gerador

`Artifact` com `action: "read"`, `url` = URL do artefato e `paths` = `["gerador/gen_semanal.py","gerador/charts.js","gerador/charts_sem.js","gerador/common.js","gerador/style.css","gerador/hist.js"]`. A pasta retornada (termina em `/gerador`) é `REL`; trabalhe sempre dentro dela e não reescreva esses arquivos.

## Passo 2 — Coletar (em paralelo, nada além disso)

1. `PGDash.relatorio_diario` com `data` = FIM e `limite_skus` = 40 (estoque de hoje, projeção, parâmetros, categorias, sincronização, nome da conta). Se falhar, avise em uma frase e pare.
2. `PGDash.consultar_overview` com `de` = INI, `ate` = FIM, `comparar_com` = `periodo_anterior`.
3. `PGDash.consultar_vendas` com `de` = FIM − 55, `ate` = FIM, `serie` = `diaria` (8 semanas).
4. `PGDash.top_produtos` com `de` = INI, `ate` = FIM, `limite` = 20.
5. `PGDash.top_produtos` com `de` = ANT_INI, `ate` = ANT_FIM, `limite` = 20.
6. `PGDash.consultar_ads` com `de` = INI, `ate` = FIM, `granularidade` = `por_campanha`, `comparar_com` = `periodo_anterior`.
7. `PGDash.consultar_visitas` para a semana e 8. para a semana anterior (só o `resumo` interessa).
9. `PGDash.consultar_tendencias` com `de` = FIM − 27, `ate` = FIM.
10. `PGDash.consultar_seo`.
11. Clima: mesma regra do Relatório diário (`clima` = auto/sempre/nunca; no `auto`, só se uma categoria de chuva, frio ou calor tiver `pct_receita` ≥ 5% ou um produto em reposição). Com a chamada: `AccuWeather.widgets-daily-claude`, `unit` = `metric`, `lang` = `pt`, próximos 7 dias a partir de HOJE.

## Passo 3 — Montar `REL/entrada.json` (com `python3`)

| Campo | Origem / regra |
|---|---|
| `conta` | parâmetro da tarefa; sem ele, `meta_dados.conta` |
| `semana_ini`, `semana_fim`, `hoje` | INI, FIM, HOJE (YYYY-MM-DD) |
| `capturado` | agora em São Paulo, `segunda, 21/09 às 07:02` |
| `sync` | `{vendas, estoque, ads}` = `meta_dados.sync_*.minutos_atras` (chamada 1) |
| `breakeven_roas` | o da tarefa |
| `sem` | chamada 2: `fat`=vendas.faturamento_liquido, `ped`=pedidos, `ticket`=ticket_medio, `un`=unidades, `mpre`=margem.margem_pre_ads, `ads`=ads.custo; chamada 7: `vis`=resumo.total_visitas, `conv`=resumo.conversao_media_pct |
| `ant` | chamada 2, `comparacao.metricas.*.anterior`: `fat`, `ped`, `ticket`, `un`, `mpre`, `ads`=custo_ads; chamada 8: `vis`, `conv` |
| `serie56` | chamada 3, `serie_diaria` como `[data, faturamento]` (56 dias, terminando em FIM) |
| `prod` | chamadas 4 e 5 casadas por `sku`: `[nome amigável, faturamento, faturamento_anterior (0 se não vendeu), unidades, margem_contrib]` |
| `ads` | chamada 6: `custo`, `receita`, `roas`, `tacos`=tacos_pct, `imp`=impressoes, `cl`=cliques, `ctr`=ctr_pct, `cpc`; `ant` = `{custo, roas, tacos}` de `comparacao.metricas.*.anterior` |
| `camp` | chamada 6, `por_campanha` com custo > 0: `[nome, impressoes, cliques, ctr_pct, cpc, custo, receita, roas]` |
| `heat`, `heat_de`, `heat_ate` | chamada 9: `heatmap` como `[dow, hora, faturamento_medio]`; FIM − 27 e FIM |
| `heat_leitura` | 1–2 frases: o bloco dia + hora mais forte (R$ por hora) e o dia mais fraco contra o mais forte (% a menos) |
| `repor` | chamada 1, `skus` com `REPOR_AGORA`/`REPOR_EM_BREVE`: `[nome, status, estoque, transito, transito_cobre_dias, qtd_sugerida, capital, comprar_ate, atraso_d]`; zerados primeiro |
| `rup` | `{n: ruptura.skus_zerados, perda: ruptura.venda_perdida_dia}` |
| `params` | `parametros_reposicao.global`: `lt`, `seg`, `alvo` |
| `proj` | chamada 1, `projecao`: `mtd`, `dec`, `rest`, `m3`=media_7d, `c3`=cenario_7d, `sem_rup`=null, `meta`, `pct_meta`, `ritmo`=ritmo_necessario. Se FIM for o último dia do mês, omita `proj` |
| `seo` | chamada 10, palavras com `variacao` ≠ 0: `[palavra em minúsculas, nome amigável do anúncio ou null, posicao, variacao]` (o anúncio sai dos `alertas` de ranqueamento da chamada 1 quando a palavra aparecer lá) |
| `clima`, `eventos`, `estacao` | mesmas regras e formatos do Relatório diário, contando os dias a partir de HOJE |
| `textos` | ver abaixo |

Nome amigável: `nome_curto` da chamada 1 quando o SKU estiver lá; senão reduza o título a tipo + variante ("Guarda-chuva Preto", "Cacto Dançante", "Blocos Magnéticos 128P"). Nunca mostre códigos de SKU.

## Passo 4 — Textos (`textos`)

- `resumo`: 3 parágrafos em HTML simples. (1) o resultado: faturamento com `<span class="hi">`, % vs semana anterior e vs média das 4 anteriores, se é a melhor ou pior das 8, e o que puxou (produto ou categoria, dia do pico). (2) a qualidade: margem pós-Ads, Ads (investimento e ROAS vs anterior), conversão e visitas, quem caiu. (3) a semana que começa: estoque zerado (perda com `<span class="hi">`), clima, data sazonal.
- `comp_leituras`: 3 leituras de até 6 palavras (semana anterior, média 4 semanas, melhor das 8).
- `camp_nota`: 1 frase — quem levou a maior parte da verba e com que ROAS, e a campanha abaixo do ponto de equilíbrio (use `<b class=b>`).
- `acoes` ("Decisões da semana"): 3 a 5, em ordem de impacto, cada uma começando com `<b>verbo + objeto.</b>` e com o número que a justifica.

Regras: nomes de produto, nunca SKU; números no formato brasileiro (R$ 64,2 mil · 7,4% · −1,1 pp); frases curtas; nada de jargão.

## Passo 5 — Gerar, publicar e guardar

```bash
cd "$REL" && python3 gen_semanal.py entrada.json "$REL/relatorio-semanal.html"
```
- Publique com `Artifact` (publish), `file_path` = `REL/relatorio-semanal.html`, `url` = URL do artefato. Não passe `files`, `icon` nem `capabilities`.
- Guarde no histórico com **uma** chamada `ArtifactData`, `action: "batch"`, `url` = URL do artefato, `writes` = `[{op:"set", collection:"edicoes", doc_id:FIM, file_path:"REL/edicao.json"}, {op:"set", collection:"indice", doc_id:FIM, file_path:"REL/indice.json"}]`. Se falhar, siga e cite a falha na mensagem.
- Envie ao cliente (SendUserMessage e, se disponível, PushNotification) no máximo 4 linhas: a primeira frase de cada parágrafo do Resumo e o link.
- Não faça outra checagem visual; o gerador já foi validado.
