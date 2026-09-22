---
name: configurar-relatorios
description: Configura ou atualiza o Relatório diário e o Relatório semanal PGDash na conta do cliente. Cria as duas páginas com histórico, agenda as tarefas das 7h e gera a primeira edição. Use quando o cliente disser "configurar relatórios", "instalar os relatórios", "ativar o relatório diário", "atualizar relatórios", ou logo depois de instalar o plugin.
---

# Configurar relatórios PGDash

Prepara, uma única vez, tudo de que os relatórios precisam na conta do cliente. Rodada de novo, atualiza as páginas com a versão do gerador que veio neste plugin.

Fale com o cliente em linguagem simples. Nunca mostre caminhos de arquivo, códigos de SKU, nomes de ferramentas nem JSON. Refira-se a ele como cliente do PGDash, nunca como "usuário".

Caminhos (uso interno):
- `BASE` é o diretório desta skill, informado quando ela carrega.
- `GER` = `BASE/gerador`.
- `SKD` = `BASE/../relatorio-diario/SKILL.md`.
- `SKS` = `BASE/../relatorio-semanal/SKILL.md`.
- `TMP` = uma pasta nova dentro do scratchpad da sessão. O Artifact só publica a partir dali ou da pasta de trabalho.

## 1. Conta PGDash

1. Chame `PGDash.relatorio_diario` com `data` = ontem (America/Sao_Paulo) e `limite_skus` = 40. Guarde a resposta: ela serve para a primeira edição.
2. Se a ferramenta não existir ou pedir login, diga ao cliente que o conector PGDash veio com o plugin e que ele precisa entrar com a conta do PGDash dele, na tela que o Claude abre. Pare aqui.
3. `CONTA` = `meta_dados.conta`. Se vier null e `meta_dados.contas` tiver mais de uma conta, avise que o relatório soma todas as contas conectadas e use os apelidos unidos por " + ".

## 2. Modo: primeira vez ou atualização

Procure as tarefas agendadas "Relatório diário · CONTA" e "Relatório semanal · CONTA" (`list_triggers`) e as páginas "Relatório diário CONTA" e "Relatório semanal CONTA" (`Artifact` `action: "list"`).
- Se as duas páginas e as duas tarefas existirem, vá para **7. Atualização**.
- Se faltar alguma parte, configure só o que falta e reaproveite o que já existe.

## 3. Parâmetros

- **Ponto de equilíbrio de ROAS:** chame `PGDash.consultar_margem_dre` com `periodo` = `30d`. `BE` = 100 ÷ `margem_pre_ads_pct`, com uma casa decimal. Se a margem vier zerada, negativa ou vazia, pergunte o número ao cliente.
- **Clima:** aplique a regra do modo `auto` descrita no Passo 2 de `SKD` à resposta do item 1.
  - Se nenhuma categoria justificar o clima: `CLIMA` = `nunca`.
  - Se justificar, descubra a cidade sozinho: chame `PGDash.consultar_vendas_regiao` com `periodo` = `30d` e pegue a primeira de `cidades`, a de maior receita. Guarde também a participação dela (receita da cidade ÷ soma da receita de `estados`) e a segunda colocada.
  - Busque o `locationKey` com `AccuWeather.widgets-search-claude` usando "cidade, UF". Se vier mais de um resultado, fique com o que tiver a mesma UF.
  - Não pergunte a cidade: ela entra no resumo de confirmação, por exemplo "Clima de São Paulo, a cidade que mais compra (12% da receita; depois vem Rio de Janeiro)". O cliente troca em "Ajustar", se quiser.
  - Se o AccuWeather não estiver conectado, procure o conector no diretório e sugira ao cliente. Se ele recusar, use `CLIMA` = `nunca` e siga.
- **Confirmação:** uma única `AskUserQuestion` com o resumo:
  - conta;
  - Relatório diário todo dia às 7h e Relatório semanal às segundas às 7h, horário de Brasília;
  - ponto de equilíbrio de ROAS;
  - clima (a cidade que mais compra e a participação dela, ou "sem clima").

  Opções: "Confirmar" e "Ajustar". Em "Ajustar", aplique o que o cliente disser.

## 4. Preparar o gerador

```bash
mkdir -p "$TMP/diario" "$TMP/semanal"
cp "$GER"/gen_diario.py "$GER"/charts.js "$GER"/common.js "$GER"/style.css "$GER"/hist.js "$TMP/diario/"
cp "$GER"/gen_semanal.py "$GER"/charts.js "$GER"/charts_sem.js "$GER"/common.js "$GER"/style.css "$GER"/hist.js "$TMP/semanal/"
cp "$SKD" "$TMP/diario/INSTRUCOES.md"; cp "$SKS" "$TMP/semanal/INSTRUCOES.md"
```

## 5. Primeira edição e páginas

**Diário:**
1. Siga os Passos 2 a 4 de `SKD`, reaproveitando a resposta do item 1. `REL` = `$TMP/diario`, `breakeven_roas` = BE, clima conforme o item 3.
2. Rode o gerador.
3. Publique uma página **nova** (sem `url`):
   - `file_path` = `$TMP/diario/relatorio-diario.html`, `icon` = `chart`;
   - `title` = "Relatório diário CONTA";
   - `description` = "Relatório diário da conta CONTA no Mercado Livre, gerado pelo PGDash";
   - `capabilities` = `{"db":{"rules":[{"path":"","read":"view","write":"admin"}]}}`;
   - `files` = `gerador/gen_diario.py` (com `contentType` `text/plain`), `gerador/charts.js`, `gerador/common.js`, `gerador/style.css`, `gerador/hist.js` e `gerador/INSTRUCOES.md` (com `contentType` `text/markdown`), cada um apontando para o arquivo de mesmo nome em `$TMP/diario`.
4. Guarde a URL como `URL_D`.
5. Grave a edição no histórico, com a chamada `ArtifactData` `batch` descrita no Passo 5 de `SKD`.

**Semanal:** faça o mesmo seguindo `SKS`, com a semana de segunda a domingo que já terminou.
- `REL` = `$TMP/semanal`, título "Relatório semanal CONTA".
- Os `files` incluem também `gerador/gen_semanal.py` e `gerador/charts_sem.js`.
- Guarde a URL como `URL_S` e grave o histórico.

Se a primeira edição falhar por falta de dado, publique a página mesmo assim com o que houver e explique ao cliente o que faltou.

## 6. Agendar

Crie duas tarefas com `create_trigger`: `initiation` = `human_request`, `notifications` = `{"push": true}`.
- "Relatório diário · CONTA": `cron_expression` = `0 10 * * *` (7h em Brasília).
- "Relatório semanal · CONTA": `cron_expression` = `0 10 * * 1`.

Texto da tarefa (troque os campos entre sinais de menor e maior):

```
Gere e publique o <Relatório diário|Relatório semanal> da conta <CONTA> no PGDash.
Carregue a skill <relatorio-diario|relatorio-semanal> do plugin PGDash Relatórios e siga os passos à risca. Se a skill não estiver disponível, leia o arquivo gerador/INSTRUCOES.md da página abaixo (Artifact, action "read", com path) e siga essas instruções.

Parâmetros desta conta:
- conta: <CONTA>
- url do artefato: <URL_D|URL_S>
- clima: <auto|nunca>
- cidade do clima: <cidade>, locationKey <chave>   (omita a linha sem clima)
- ponto de equilíbrio de ROAS: <BE>
<só no semanal:> - url do relatório diário: <URL_D>
<só no semanal:> A semana é a de segunda a domingo que terminou ontem.

Não faça perguntas: rode sem interação. Se alguma etapa falhar, envie ao cliente uma única linha dizendo o que falhou.
```

Depois de criar, diga em uma frase como as tarefas vão rodar: com aprovação automática ou pedindo aprovação. Se forem pedir, explique que o cliente pode ligar "Aprovar automaticamente" nas configurações de cada tarefa, porque às 7h não haverá ninguém para aprovar.

## 7. Atualização

Para cada página, pegue a URL no texto da tarefa correspondente:
1. `Artifact` `action: "read"` com a `url`. O resultado indica o arquivo salvo com a página atual.
2. Publique com `url`, `file_path` = esse arquivo e `files` = os arquivos do gerador de `$TMP/diario` ou `$TMP/semanal` (item 4), incluindo `INSTRUCOES.md`.
3. Não passe `capabilities` nem `icon`: o histórico e o ícone continuam como estão.

Reescreva o texto de uma tarefa com `update_trigger` só se ele não seguir o modelo do item 6.

Diga ao cliente que as páginas foram atualizadas, que o histórico foi mantido e que o visual novo aparece a partir da próxima edição.

## 8. Fechamento

Termine com no máximo 4 linhas:
- o que foi criado (as duas páginas, com o link de cada uma);
- quando chegam (diário às 7h, semanal às segundas às 7h, com aviso no celular);
- clima ligado ou não;
- ponto de equilíbrio usado.

Lembre que ele pode pedir "relatório de ontem" a qualquer momento.
