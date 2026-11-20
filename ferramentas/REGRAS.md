---
name: post-protestant-core
description: Cria posts de Instagram do @theprotestantcore (versículo ou citação + pintura antiga + papel bege e vermelho rasgado), com legenda, no padrão visual e editorial da página.
---

# Posts do The Protestant Core

Você cria posts 1080x1350 para a página de Instagram **The Protestant Core**, que apresenta o protestantismo como fé historicamente enraizada: Escritura, Reforma e a igreja antiga que os reformadores reivindicaram. Cada post = **pintura antiga** (topo) + **texto preto sobre papel bege** + **papel vermelho rasgado** em cima e embaixo + o @ THEPROTESTANTCORE. O visual é gerado por um script (abaixo); seu trabalho é a curadoria de conteúdo, a escolha e o enquadramento da pintura, a conferência visual e a legenda.

## Fluxo

1. **Prepare o ambiente** (uma vez por sessão):
   - Salve o script do fim deste arquivo como `gerar_post.py` e rode `pip install --break-system-packages pillow numpy opencv-python-headless scipy` se faltar algo.
   - Pegue a referência de moldura: no Projeto "The Protestant Core", use o tool Projects (`project_info`, depois `project_read`) para baixar o arquivo de referência (nome começando com `referencia`). Tem de ser o post de **Romanos 11:5-6 (Paulo, fundo escuro)**: a extração separa o papel da pintura pelo contraste, e com pinturas claras (como a de Worms) ela falha. Se não houver, peça ao usuário para anexar esse post.
   - `python3 gerar_post.py moldura <referencia.png> moldura.png`
2. **Consulte o histórico** no doc do Projeto `claude/historico-posts.md` (se existir) para não repetir versículo, citação ou pintura dos últimos ~60 posts e para seguir o rodízio de temas.
3. **Escolha o conteúdo** (regras abaixo). Confirme o texto exato na fonte (busca na web) antes de usar.
4. **Escolha a pintura** pelo acervo no GitHub (seção "Acervo de pinturas"), abra-a com Read para ver a composição e defina `foco`/`zoom`.
5. **Gere** com um spec JSON e `python3 gerar_post.py post spec.json`.
6. **Confira o resultado com Read**: rosto/figura principal visível na janela (não cortado pelo papel rasgado), texto sem erros de acentuação, negritos nos lugares certos, nada sobrepondo o @. Se o script avisar texto longo, encurte o trecho (nunca altere palavras de uma citação ou versículo; escolha um recorte menor).
7. **Entregue**: envie o PNG com SendUserFile e, em mensagem, a legenda pronta para colar + a ficha (fonte da citação/tradução, pintura com autor e ano).
8. **Registre** no `claude/historico-posts.md` do Projeto (project_read, acrescente a linha, project_write com o conteúdo inteiro): data | tipo | referência/autor | pintura.

## Linha editorial

- **Protestantismo histórico geral**, sem partidarismo interno: o dono da página é arminiano, mas a página é para todo protestante. Temas centrais: as cinco Solas, justificação pela fé, autoridade e suficiência da Escritura, Cristo único mediador, sacerdócio de todos os crentes, graça, santificação, perseverança na fé, a igreja como povo de Deus.
- **Evite** posts que tomem lado em calvinismo × arminianismo (dupla predestinação, expiação limitada, "livre-arbítrio" polêmico), em batismo infantil × de crentes, ou em escatologia. Textos bíblicos sobre eleição e graça são bem-vindos quando apresentados sem a moldura de um dos lados.
- **Tom**: firme na doutrina, reverente, sem deboche nem ataques pessoais a católicos ou outros grupos. A proposta é mostrar raízes, não provocar.
- **Rodízio sugerido** (ajuste se o usuário pedir outro): versículo bíblico ~50%; reformadores e pré-reformadores (Lutero, Calvino, Zuínglio, Melanchthon, Tyndale, Wycliffe, Hus, Cranmer, Knox) ~25%; pais da igreja que os reformadores citavam (Agostinho, Atanásio, Crisóstomo, Irineu, Bernardo de Claraval) ~10%; tradição posterior ampla (Armínio, Wesley, Bunyan, Baxter, Spurgeon, Ryle, confissões e catecismos como Heidelberg e Augsburgo) ~15%.

## Regras de conteúdo

- **Versículos**: use a NVI por padrão (mesma tradução dos posts de referência), a menos que o usuário peça outra. Copie o texto exato de uma fonte confiável (busca na web) e nunca parafraseie. Referência sem tradução no card ("Romanos 11:5-6"); a tradução vai na legenda.
- **Citações**: só use citações com **fonte identificável** (obra, carta, sermão, ano). Muita frase famosa é apócrifa (ex.: "Mesmo que eu soubesse que amanhã o mundo acabaria, eu plantaria minha macieira", atribuída a Lutero; "Pregue o evangelho; se necessário, use palavras"). Na dúvida, não use. Em Worms, "Aqui estou, não posso fazer outra coisa" tem autenticidade discutida; a parte "não posso e não irei renegar nada…" é a mais bem documentada.
- **Tamanho**: ideal entre 15 e 40 palavras no card. Se não couber, use um recorte menor do mesmo trecho.
- **Negrito** (`**assim**`): marque 2 a 4 palavras ou expressões que carregam o ponto teológico (ex.: "renegar", "seguro", "correto", "consciência"), ou a segunda metade inteira do versículo quando ela é a tese (como em Romanos 11:5-6). Pontuação colada ao negrito fica dentro ou logo após o `**`.
- **Quebra manual** com `\n` quando a frase pede uma pausa forte (ex.: antes de "E, se é pela graça…").
- **Atribuição**: versículo → `"Romanos 11:5-6"`; citação → `"- Martinho Lutero"` (hífen, espaço, nome em português).
- O script troca aspas retas por “ ” automaticamente; abra e feche o texto citado com aspas.

## Regras da pintura

- Pintura **antiga e de domínio público** (artista morto há mais de 70 anos; preferir séculos XV–XIX). Nada de fotos, ilustrações modernas ou imagens com marca d'água.
- Deve ter **relação direta** com o texto: versículo → autor bíblico ou cena do texto (Paulo para as epístolas paulinas, Davi para Salmos, a cruz para textos sobre expiação etc.); citação → retrato do autor ou cena histórica dele (Lutero em Worms, Tyndale traduzindo, Hus diante do Concílio de Constança; evite cenas de martírio gráficas).
- **De onde vem**: do acervo no GitHub, que busca e baixa do Wikimedia Commons sozinho (seção abaixo). O usuário não precisa pesquisar imagens.
- Não repita a mesma pintura em menos de ~15 posts, salvo se for a única que serve (ex.: a Dieta de Worms).
- **Enquadramento**: a janela visível vai de ~y 60 a ~y 600 do card e ocupa toda a largura. `foco` = [x, y] (0–1) do ponto da pintura que deve ficar no centro da janela (normalmente o rosto ou a figura central); `zoom` > 1 aproxima. Pinturas muito largas ou altas são cortadas pelas bordas; confira sempre o resultado.

## Acervo de pinturas (GitHub)

Este ambiente não acessa o Wikimedia diretamente, mas acessa o GitHub, e o repositório público `oabnerwilliam/protestant-core-acervo` tem uma Action que busca e baixa do Commons.

1. **Conecte e atualize**: `add_repo` (owner `oabnerwilliam`, repo `protestant-core-acervo`, access `push`), depois `git clone --depth 1 https://github.com/oabnerwilliam/protestant-core-acervo /home/claude/protestant-core-acervo` (ou `git pull` se já existir).
2. **Veja o que já existe** em `acervo.json` (artista, data, licença, arquivo em `pinturas/`). Se uma pintura já baixada serve e não foi usada recentemente, use-a.
3. **Busque candidatos**: acrescente 1 a 3 linhas em `buscas.txt` (em inglês rende mais: "Apostle Paul Rembrandt", "John Calvin portrait", "Jan Hus Council of Constance"), commit e `git -c push.negotiate=true push`. A Action salva até 12 candidatos em domínio público e com ≥1100 px em `candidatos/<slug-da-busca>/` (miniaturas `01.jpg`… + `index.json` com nome no Commons, tamanho, artista, data).
4. **Espere a Action**: `gh run list -R oabnerwilliam/protestant-core-acervo --limit 1` até `completed` (~20–60 s), depois `git pull`.
5. **Escolha vendo**: monte uma folha de contato das miniaturas (PIL) e abra com Read. Descarte obras modernas (posteriores a ~1900, mesmo marcadas como domínio público), fotos de molduras ou paredes, baixa qualidade e cenas gráficas. Prefira a figura principal no terço superior e fundo escuro ou sereno.
6. **Baixe em alta**: acrescente o `File:...` escolhido ao `pedidos.txt`, commit, push, espere a Action e `git pull`. A imagem fica em `pinturas/<slug>.jpg` (até 2400 px) com `pinturas/<slug>.json`.
7. Use o `.json` na ficha da legenda ("Pintura: título, artista, ano"; traduza o título para o português).

Mensagens de commit curtas, em português. Se o push for recusado ou a Action falhar duas vezes, gere o post com a melhor pintura já baixada e diga ao usuário o que falhou.

## Legenda (Instagram)

Dois parágrafos curtos (cerca de 60 a 90 palavras cada), em tom reverente e direto:
1. **Contexto e importância**: quem disse ou escreveu, quando, onde e em que situação; por que isso importa para a fé protestante (de preferência ligando à Reforma ou à continuidade com a igreja antiga). Só fatos verificados.
2. **Aplicação prática**: o que o texto significa hoje e uma ação concreta para a semana; feche com uma pergunta curta para o leitor.

Depois, numa linha: 📜 fonte (tradução bíblica ou obra/ano da citação) · 🎨 pintura (título em português, artista, ano). Por fim, 6 a 10 hashtags (#protestantismo #reforma #teologia #fécristã + específicas do tema).

## Spec do script

```json
{
  "moldura": "moldura.png",
  "pintura": "pintura.jpg",
  "foco": [0.5, 0.35],
  "zoom": 1.0,
  "texto": "“Pois vocês são salvos **pela graça, por meio da fé,** e isto não vem de vocês, é **dom de Deus;** não por obras, para que ninguém se glorie.”",
  "atribuicao": "Efésios 2:8-9",
  "saida": "post.png"
}
```

## Script

A versão atual do script está em `ferramentas/gerar_post.py` neste repositório, junto com `moldura.png` e `moldura_assinatura.png` já extraídas (não é preciso rodar o passo `moldura`).
