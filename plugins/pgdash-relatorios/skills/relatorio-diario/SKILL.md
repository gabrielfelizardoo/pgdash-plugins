---
name: relatorio-diario
description: Gera e publica o Relatório diário de vendas no Mercado Livre a partir do PGDash (e do clima do AccuWeather, quando a conta vende produto sensível a clima). Use quando a tarefa agendada ou o cliente pedir o "relatório diário", "relatório da manhã" ou "relatório de ontem".
---

# Relatório diário PGDash

Relatório de 90 segundos sobre o dia anterior de uma conta do Mercado Livre, para profissionais de operação. O visual e o cálculo já estão prontos no gerador anexado ao artefato do relatório: seu trabalho é **coletar, mapear para o JSON de entrada, escrever os textos e publicar**. Não recrie o HTML à mão.

Os parâmetros da conta (nome da conta, URL do artefato, `clima` = auto/sempre/nunca, cidade do clima com `locationKey`, ponto de equilíbrio de ROAS) vêm da tarefa agendada que chamou esta skill. Quando o cliente pedir o relatório fora da tarefa, procure a página dele com `Artifact` `action: "list"` (título "Relatório diário <conta>") e use os parâmetros da tarefa agendada "Relatório diário · <conta>" (`list_triggers`). Se não houver página, diga em uma frase que é preciso rodar "configurar relatórios" antes e pare.

## Passo 1 — Baixar o gerador (sem reescrever código)

O gerador fica anexado ao próprio artefato do relatório (URL informada pela tarefa). Baixe os 5 arquivos numa única chamada:

`Artifact` com `action: "read"`, `url` = URL do artefato e `paths` = `["gerador/gen_diario.py","gerador/charts.js","gerador/common.js","gerador/style.css","gerador/hist.js"]`.

O resultado informa a pasta onde os arquivos foram salvos (dentro do scratchpad, terminando em `/gerador`). Chame essa pasta de `REL` e trabalhe sempre dentro dela: é o único lugar de onde o Artifact aceita publicar. Não reescreva nenhum desses arquivos à mão.

## Passo 2 — Coletar (até 3 chamadas, nada além disso)

1. `PGDash.relatorio_diario` com `data` = ontem no fuso America/Sao_Paulo e `limite_skus` = 40. Se falhar, avise o cliente em uma frase e pare.
2. `PGDash.consultar_ads` com `granularidade` = `por_dia`, `de` = 13 dias antes de ontem, `ate` = ontem (só para a linha de CTR de 14 dias).
3. Clima — decida pelo parâmetro `clima` da tarefa (padrão `auto`); sem clima, não chame o AccuWeather e use `clima: null`:
   - `sempre`: chame (tipo `chuva`, a menos que a tarefa diga outro).
   - `nunca`: não chame.
   - `auto`: chame **só se** a conta vende algo sensível ao clima. Use as categorias do Mercado Livre que o `relatorio_diario` já devolve: o bloco `categorias` (receita de 28 dias por categoria, com `pct_receita` e `caminho`) e `skus[].categoria`. Compare o nome da categoria e o `caminho` (sem acento, minúsculas, singular ou plural) com os grupos abaixo. A categoria **justifica** o clima quando tem `pct_receita` ≥ 5% **ou** algum SKU dela está em `REPOR_AGORA`/`REPOR_EM_BREVE`. Sem categoria (null), use o nome do produto.
     - `chuva`: guarda-chuva, sombrinha, capa de chuva, galocha, bota de chuva, capa impermeável.
     - `frio`: aquecedor, cobertor, manta, edredom, casaco, jaqueta, luva, gorro, cachecol, meia térmica, segunda pele.
     - `calor`: ventilador, climatizador, ar-condicionado, protetor solar, piscina, boia, cooler, umidificador.
     Com mais de um grupo justificado, fique com o de maior `pct_receita`. Se nenhum justifica, não chame.
   - A tarefa pode fixar grupos extras (`clima_produtos: ...`); some-os aos acima.
   Com a chamada: `AccuWeather.widgets-daily-claude` com o `locationKey` da cidade (se não tiver a chave, `widgets-search-claude` antes), `unit` = `metric`, `lang` = `pt`.

## Passo 3 — Montar `REL/entrada.json`

Escreva o JSON com `python3` (não à mão em HTML). Campos, de onde vêm e regras:

| Campo | Origem / regra |
|---|---|
| `conta` | parâmetro da tarefa; sem ele, `meta_dados.conta` |
| `data` | a `data` do relatório (YYYY-MM-DD) |
| `capturado` | agora em São Paulo, formato `sábado, 19/09 às 07:02` |
| `sync` | `{vendas, estoque, ads}` = `meta_dados.sync_*.minutos_atras` |
| `breakeven_roas` | o da tarefa |
| `dia` | `fat`=faturamento, `ped`=pedidos, `ticket`, `un`=unidades, `mpre`=margem_pre_ads, `mpos`=margem_pos_ads, `ads`=custo_ads, `vs_d1`=vs_d1_pct, `vs_d7`=vs_d7_pct, `vs_m7`=vs_media7d_pct, `mediana`=mediana_4_mesmo_dow, `vs_med`=vs_mediana_pct, `d7_atip` |
| `funil` | `imp`=impressoes, `cl`=cliques, `ctr`=ctr_pct, `vis`=visitas, `conv`=conversao_pct |
| `serie` | `serie_28d` como `[data, faturamento, mm7]` |
| `ctr14` | `consultar_ads.serie_diaria` como `["DD/M", clicks, impressoes]` |
| `camp` | `campanhas` como `[nome, impressoes, cliques, ctr_pct, cpc, custo, receita, roas]` (roas pode ser null) |
| `proj` | `mtd`, `dec`=dias_decorridos, `rest`=dias_restantes, `m3`=media_3d, `c3`=cenario_3d, `sem_rup`=cenario_sem_ruptura, `meta`, `pct_meta`, `ritmo`=ritmo_necessario |
| `rup` | `n`=skus_zerados, `perda`=venda_perdida_dia, `perda_mes`=venda_perdida_ate_fim_mes, `prox`=nome amigável do `proximo_a_zerar`, `prox_tr`=trânsito desse SKU |
| `params` | `lt`, `seg`, `alvo` = `parametros_reposicao.global` (lead_time_dias, seguranca_dias, cobertura_alvo_dias) |
| `skus` | só `REPOR_AGORA` e `REPOR_EM_BREVE`, como `[nome, estoque, transito, media_diaria, tendencia_pct, cobertura_d, data_ruptura, qtd_sugerida, capital, venda_perdida_dia, transito_cobre_dias]`. Ordem: zerados por perda decrescente, depois por cobertura crescente |
| `cap_total` | soma de `capital` das linhas acima |
| `seo` | dos `alertas` com `tipo`=`ranqueamento`, até 3, maior queda primeiro: `[palavra em minúsculas, nome amigável do anúncio, posição atual, -queda, posição anterior]` |
| `clima` | ver regra abaixo, ou `null` |
| `eventos`, `estacao` | ver calendário abaixo; `[]` e `null` quando nada se aplica |
| `marcos` | até 2 marcas no gráfico de 28 dias, `[data, rótulo curto]` (ex.: início de um pico, primeiro dia de ruptura). `[]` se não houver nada claro |
| `textos` | ver regras de escrita |

**Nome amigável:** use `nome_curto`; se vier o título do anúncio, reduza para tipo + variante ("Guarda-chuva Preto", "Blocos Magnéticos 96P", "Kit 2 Munhequeiras"). Nunca mostre códigos de SKU.

**Clima:** `{cidade, tipo: "chuva"|"frio"|"calor", afeta: "Afeta os <produtos> (<pct_receita da categoria>% da receita · <n> produtos).", alerta: texto HTML do alerta do INMET ou null, dias: 7 itens, nota: 1 frase ligando o clima e o estoque desses produtos}`. Cada dia = `["sáb 19", prob_chuva_do_dia, ícone, temperatura, alerta_bool]`, com temperatura = máxima (`"26°"`) para `chuva` e `calor`, mínima para `frio`. O gerador destaca o dia com chuva ≥ 50%, mínima ≤ 12° ou máxima ≥ 32°, conforme o tipo; ícone `storm` se probabilidade de trovoada ≥ 30%, `rain` se chuva ≥ 50%, `sun` se chuva < 20% e nuvens < 40%, senão `cloud`; `alerta_bool` quando a data está em algum alerta.

**Calendário** (mostre só datas dentro de 70 dias **e** com produto relacionado na conta — decida pela `caminho` das `categorias` com `pct_receita` ≥ 2% e pela `skus[].categoria`: "Brinquedos e Hobbies" relaciona Dia das Crianças e Natal; "Beleza e Cuidado Pessoal", "Joias e Relógios" e "Calçados, Roupas e Bolsas" relacionam Mães, Namorados, Pais e Natal; "Papelaria" e mochilas, Volta às aulas):
Dia das Mães (2º domingo de maio) · Dia dos Namorados (12/06) · Dia dos Pais (2º domingo de agosto) · Dia das Crianças (12/10: brinquedos, jogos) · Black Friday (última sexta de novembro: todos) · Natal (25/12: presentes, brinquedos) · Volta às aulas (1ª semana de fevereiro: papelaria, mochilas). Cada evento: `{nome, data, cor: "crit" se a data de compra já passou ou é em até 7 dias, senão "info", comprar_ate: data − 14 dias de folga − (lt+seg), itens: [[texto, nível do chip ou "", texto do chip ou valor]], rodape}`. Itens: um por produto relacionado com o status do estoque até a data ("cobre", "acaba DD/MM", "zerado"); para "todos os produtos", use as linhas "Comprar até" e "Estoque no Full". `estacao` = `{inicio: "YYYY-10-01", texto: "estação de chuvas · <produtos>"}` entre setembro e março quando o tipo do clima é `chuva`; para `frio`, `{inicio: "YYYY-06-21", texto: "inverno · <produtos>"}` entre abril e agosto; para `calor`, `{inicio: "YYYY-12-21", texto: "verão · <produtos>"}` entre outubro e fevereiro. Nos outros casos (inclusive sem clima), `null`.

## Passo 4 — Escrever os textos (`textos`)

- `resumo`: 3 parágrafos em HTML simples. (1) o que aconteceu: faturamento com `<span class="hi">`, % vs dia anterior e vs mediana do dia da semana; conversão e visitas dizem se o problema é tráfego ou anúncio; % da meta quando houver. (2) a causa dominante (ruptura: perda por dia com `<span class="hi">` e até o fim do mês; o trânsito que resolve). (3) próximos riscos: o que zera, clima/alerta (só se houver bloco de clima), data sazonal na janela.
- `comp_leituras`: 4 leituras de até 6 palavras (dia anterior, mediana, média 7 dias, dia da semana anterior).
- `camp_nota`: 1 frase — melhor retorno e a campanha que gastou sem vender (use `<b class=b>`).
- `acoes`: 3 ações em ordem de impacto, cada uma começando com `<b>verbo + objeto</b>` e com o número que a justifica.

Regras: nomes de produto, nunca SKU; sem jargão ("prazo de reposição", "acaba em", "venda por dia"); nunca "D-1/D-7"; números no formato brasileiro (R$ 1,9 mil · 7,7%); frases curtas.

## Passo 5 — Gerar e publicar

```bash
cd "$REL" && python3 gen_diario.py entrada.json "$REL/relatorio-diario.html"
```
- Publique com `Artifact` (publish), `file_path` = `REL/relatorio-diario.html` e `url` = URL do artefato da tarefa. Isso atualiza a mesma página e mantém os arquivos do gerador anexados. Não passe `files`, `icon` nem `capabilities`.
- Guarde a edição no histórico da página: o gerador também grava `REL/edicao.json` e `REL/indice.json`. Faça **uma** chamada `ArtifactData` com `action: "batch"`, `url` = URL do artefato e `writes` = `[{op:"set", collection:"edicoes", doc_id:<data>, file_path:"REL/edicao.json"}, {op:"set", collection:"indice", doc_id:<data>, file_path:"REL/indice.json"}]` (troque `REL` pelo caminho real e `<data>` pela data do relatório, YYYY-MM-DD). Sem essa gravação, o dia não aparece na navegação "Dias anteriores". Se a gravação falhar, publique mesmo assim e cite a falha na mensagem.
- Depois, envie ao cliente (SendUserMessage e, se disponível, PushNotification) no máximo 4 linhas: a primeira frase de cada parágrafo do Resumo, em texto simples, e o link.
- Não faça nenhuma outra checagem visual; o gerador já foi validado.
