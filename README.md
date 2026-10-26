# Minha pequena linguagem

Trabalho semestral de **Compiladores** — Ciência da Computação, UNISAGRADO.
Prof. Luiz Ricardo Mantovani da Silva · 2026-2

Cada grupo escreve um **compilador completo** para a MPL, uma linguagem
pequena de palavras-chave em português. O compilador de vocês vai ler um
programa em `.mpl`, atravessar as quatro fases da disciplina e produzir um
arquivo que **roda de verdade** numa máquina virtual que vocês também vão
escrever.

No fim do semestre vocês executam um programa escrito por vocês, numa
linguagem compilada por vocês.

---

## Comece por aqui

```bash
git clone https://github.com/LuizRMSilva1973/compiladores-lab.git
cd compiladores-lab
```

```bash
make verificar E=1
```

Vai dar vermelho — é para dar. O esqueleto responde à linha de comando mas
ainda não tem nenhuma fase escrita. O vermelho é o seu ponto de partida, e
ele vai virando verde conforme vocês preenchem `mplc/`.

Não precisa instalar nada além do Python 3. Se o notebook de vocês der
trabalho, o [Google Cloud Shell](https://shell.cloud.google.com) já vem com
Python 3.12, Java 21 e git — e é o mesmo ambiente da correção.

---

## Os três documentos que mandam

| Arquivo | O que decide |
|---|---|
| [LINGUAGEM.md](LINGUAGEM.md) | **o que** o compilador aceita: a sintaxe e as regras de tipo da MPL |
| [CONTRATOS.md](CONTRATOS.md) | **como** ele se comunica: a linha de comando e o formato de cada despejo |
| [entregas/](entregas/) | o enunciado de cada entrega, com o que vale nota |

Quando a sua intuição discordar de um deles, é o arquivo que vale. Se o
arquivo estiver errado, me procurem — já aconteceu de eu escrever um exemplo
errado no contrato e só descobrir rodando.

---

## As entregas

| # | Entrega | Turma A (quarta) | Turma B (segunda) | Vale |
|---|---|---|---|---|
| [E1](entregas/E1.md) | Analisador léxico | 02/09 | 31/08 | 0,8 |
| [E2](entregas/E2.md) | Analisador sintático e árvore | 30/09 | 28/09 | 1,2 |
| [E3](entregas/E3.md) | Tabela de símbolos e tipos | 28/10 | 26/10 | 1,2 |
| [E4](entregas/E4.md) | Código intermediário, geração e VM | 18/11 | 16/11 | 1,8 |
| [Apres.](entregas/APRESENTACAO.md) | Demonstração e defesa | 25/11 | 23/11 | 1,0 |

São **quatro entregas sobre o mesmo compilador**, não quatro trabalhos. O que
vocês escreverem na E1 continua rodando na E4 — e o verificador da E4 confere
tudo o que veio antes. Deixar a E1 pela metade custa caro em novembro.

---

## Regras do jogo

**A entrega é o repositório, nunca a máquina de vocês.** A correção clona o
repositório numa máquina limpa e roda `make verificar E=n`. Se não passar
lá, não conta como entregue. Testem antes de entregar — de preferência na
Cloud Shell, que é o ambiente da correção.

**Grupos de até 3.** O mesmo grupo do começo ao fim. Mudança de grupo só até
a E1.

**Gerador de parser proibido nas Entregas 1 e 2.** ANTLR, PLY, yacc, lark e
parentes escondem exatamente a parte que está sendo ensinada. Da E3 em diante
o assunto é outro, e aí não faz diferença. Na apresentação vocês podem — e
devem — comparar o parser de vocês com o que um gerador produziria.

**A linguagem de implementação é de vocês, entre as que o ambiente da correção
já tem:** Python 3.12, Java 21, C e C++ (gcc 13), Ruby 3.2 ou PHP 8.3. O
verificador não olha para dentro — ele roda `./compilar` e `./executar` e
compara o que sai. O esqueleto em `mplc/` é Python porque é o caminho mais
curto, mas ninguém é obrigado a usá-lo.

A lista existe por um motivo prático: a correção roda numa Cloud Shell limpa, e
o que não estiver lá não roda. Querem outra linguagem? Falem comigo **antes** de
começar — o critério é ela existir no ambiente sem instalação. Em nenhum caso
dependam de biblioteca externa: só a biblioteca padrão.

**Escrever o compilador é a tarefa.** Usar IA para explicar um conceito,
revisar uma mensagem de erro ou entender um trecho é bem-vindo, e eu faço
isso também. Entregar um compilador que vocês não sabem alterar é outra
coisa — e a apresentação foi desenhada para separar os dois casos: cada grupo
recebe **uma alteração pequena na linguagem, na hora, com 10 minutos para
fazer**. Quem escreveu o compilador faz. Não é desconfiança; é o formato.

---

## O verificador

```bash
make verificar E=2      # confere a Entrega 2 e, junto, a 1
make verificar          # confere as quatro
make evidencias E=2     # grava evidencias/verificacao-2.txt, que vai na entrega
```

**Antes de entregar, rodem `make prova`.** Ele clona o repositório de vocês num
diretório limpo e verifica lá — que é exatamente o que a correção faz. É o
teste que pega o defeito mais comum de todos, e que não tem nada a ver com
compiladores: *funciona aqui e não no clone*. Arquivo esquecido fora do commit,
caminho absoluto, passo de compilação que ninguém roda. Vale para qualquer
linguagem, e é a única prova que realmente antecipa a correção.

Ele não lê o código de vocês. Ele roda o compilador e compara a saída com um
corpus de **10 programas válidos**, **26 programas que precisam ser
recusados na compilação** e **3 que precisam falhar na execução** — com a
fase e a linha do erro conferidas.

Os programas recusados são metade da nota escondida do trabalho. Um
compilador que aceita tudo passa em todos os testes positivos e não vale
nada: é por isso que o corpus tem mais programas errados do que certos.

**A correção usa um segundo corpus, que vocês não têm.** Mesma linguagem,
mesmas regras, programas diferentes. Um compilador de verdade passa nos dois
sem que vocês precisem fazer nada; um programa que apenas reproduza as saídas
esperadas deste corpus passa aqui e reprova lá. Estou dizendo isto abertamente
para ninguém perder tempo pelo caminho errado.

---

## Como entregar

1. `git push` no repositório do grupo.
2. Abram a [página do trabalho](https://profluiz.mantovanitec.com/disciplinas/aulas/compiladores/trabalho.html).
3. No formulário do fim da página: escolham a entrega, identifiquem os
   integrantes (nome, RA e e-mail), colem a URL do repositório e anexem o
   `evidencias/verificacao-N.txt`.
4. Cada integrante recebe uma cópia por e-mail. **Guardem esse e-mail**: é o
   comprovante.

---

# Documentação do grupo

Compilador em Python 3, só biblioteca padrão. As fases ficam em `mplc/`:
`lexico.py` → `sintatico.py` → `semantica.py` → `intermediario.py` → `gerador.py`, e a máquina virtual em `vm.py`.

```bash
./compilar exemplos/grupo.mpl && ./executar exemplos/grupo.mplb
```

## Entrega 1 — Tabela de tokens

O analisador léxico (`mplc/lexico.py`) é um autômato escrito à mão: olha o primeiro caractere e decide qual reconhecedor chamar. Espaços (` `, `\t`, `\r`, `\n`) e comentários são descartados antes de cada token.

| Tipo | Expressão regular / regra | Exemplo |
|---|---|---|
| `INTEIRO` | `[0-9]+` | `42` |
| `REAL` | `[0-9]+\.[0-9]+` (dígito obrigatório dos dois lados) | `3.14` |
| `LOGICO` | `verdadeiro \| falso` | `falso` |
| `TEXTO` | `"([^"\\\n] \| \\[nt"\\])*"` | `"a\nb"` |
| `ID` | `[a-zA-Z_][a-zA-Z0-9_]*` que não seja palavra reservada | `soma` |
| `FUNCAO` `RETORNE` `SE` `SENAO` `ENQUANTO` `ESCREVA` | a palavra exata | `senao` |
| `TIPO_INTEIRO` `TIPO_REAL` `TIPO_LOGICO` `TIPO_TEXTO` `TIPO_VAZIO` | `inteiro`, `real`, `logico`, `texto`, `vazio` | `real` |
| `E` `OU` `NAO` | `e`, `ou`, `nao` | `nao` |
| `MAIS` `MENOS` `VEZES` `DIVIDE` `RESTO` | `+` `-` `*` `/` `%` | |
| `IGUAL` `DIFERENTE` `MENOR_IGUAL` `MAIOR_IGUAL` | `==` `!=` `<=` `>=` (testados **antes** dos de um caractere) | |
| `MENOR` `MAIOR` `ATRIBUI` | `<` `>` `=` | |
| `ABRE_PAR` `FECHA_PAR` `ABRE_CHAVE` `FECHA_CHAVE` `VIRGULA` `PONTO_VIRGULA` | `(` `)` `{` `}` `,` `;` | |
| `FIM_ARQUIVO` | fim do texto | |
| *(descartado)* | `//[^\n]*` e `/\*(.|\n)*?\*/` (não aninha) | |

Erros léxicos e onde são apontados:

| Erro | Posição |
|---|---|
| escape inválido (`\q`) | a barra invertida |
| `3.` (sem dígito depois do ponto) | o ponto |
| `.5` (sem dígito antes do ponto) | o ponto |
| texto não fechado na linha | a aspa de abertura |
| comentário de bloco não fechado | o `/*` onde ele começou |
| caractere desconhecido (`@`, `!` sozinho...) | o caractere |

## Entrega 2 — Gramática (EBNF)

```ebnf
programa     = { funcao } FIM_ARQUIVO ;
funcao       = "funcao" tipo_retorno ID "(" [ parametro { "," parametro } ] ")" bloco ;
parametro    = tipo ID ;
tipo         = "inteiro" | "real" | "logico" | "texto" ;
tipo_retorno = tipo | "vazio" ;

bloco        = "{" { comando } "}" ;
comando      = declaracao | atribuicao | chamada ";" | se | enquanto
             | escreva | retorne | bloco ;
declaracao   = tipo ID [ "=" expressao ] ";" ;
atribuicao   = ID "=" expressao ";" ;
se           = "se" "(" expressao ")" bloco [ "senao" bloco ] ;
enquanto     = "enquanto" "(" expressao ")" bloco ;
escreva      = "escreva" "(" expressao ")" ";" ;
retorne      = "retorne" [ expressao ] ";" ;

expressao    = ou ;
ou           = e          { "ou" e } ;
e            = igualdade  { "e" igualdade } ;
igualdade    = relacional { ( "==" | "!=" ) relacional } ;
relacional   = aditiva    { ( "<" | "<=" | ">" | ">=" ) aditiva } ;
aditiva      = multiplic  { ( "+" | "-" ) multiplic } ;
multiplic    = unaria     { ( "*" | "/" | "%" ) unaria } ;
unaria       = ( "nao" | "-" ) unaria | primaria ;
primaria     = INTEIRO | REAL | LOGICO | TEXTO | ID | chamada | "(" expressao ")" ;
chamada      = ID "(" [ expressao { "," expressao } ] ")" ;
```

A precedência está na própria forma da gramática: cada nível só chama o nível
**imediatamente mais forte**, então o operador mais fraco fica mais perto da raiz.
A repetição `{ op x }` é um laço que vai pendurando a árvore à **esquerda**
(associatividade à esquerda); só `unaria` chama a si mesma, e por isso `nao` e
`-` unário associam à direita. No código, os seis níveis binários são uma tabela
(`NIVEIS` em `sintatico.py`) percorrida por uma única função `binario(nivel)`.
Para distinguir `x = ...` de `f(...)` como comando, o parser olha um token à
frente (LL(2) só nesse ponto).

## Entrega 3 — Estrutura dos escopos

Cada escopo é um objeto com um dicionário de símbolos e um ponteiro para o
escopo pai (um **dicionário encadeado**). A busca de um nome sobe a cadeia até o
global, e é isso que dá o sombreamento: o `x` de dentro é encontrado primeiro, e
quando o bloco termina o analisador simplesmente volta a usar o escopo pai, e o
`x` de fora reaparece. Todos os escopos também ficam numa lista, na ordem em que
abrem, que é exatamente a ordem que o `--tabela` imprime. Escolhemos isso em vez
de uma pilha que descarta o escopo ao fechar porque precisamos guardar todos
para o despejo e para a geração de código.

São duas passadas: a primeira coleta só as assinaturas das funções no escopo 0
(por isso uma função pode ser chamada antes de aparecer); a segunda percorre os
corpos. Para a Entrega 4, cada variável ganha um nome único dentro da função
(`x`, `x#2`, `x#3`...), que depois vira um número de slot no registro de ativação.

A garantia de retorno é estrutural: um bloco garante retorno se algum comando
dele garante; `retorne` garante; `se` só garante se tiver `senao` e os dois lados
garantirem; `enquanto` nunca garante.

## Entrega 4 — Código intermediário e máquina virtual

O `--ir` é código de três endereços com temporários `tN`, rótulos `LN:`,
`seFalso t desvie L`, `param`/`chama` e `# linha N` (marca de linha, usada pela
VM para relatar erros de execução). A conversão `inteiro → real` é uma
instrução própria (`t = real a`), inserida pela semântica **depois** da
operação; por isso `real x = 7 / 2;` dá `3.000000`.

O `.mplb` é texto. Cada função começa com `funcao <nome> <nº params> <nº locais>`,
seguido de linhas `local <slot> <nome>` (só documentação) e termina em `fim`.

### Conjunto de instruções da VM (máquina de pilha)

| Instrução | O que faz com a pilha |
|---|---|
| `empilha <constante>` | empilha um inteiro, real, `verdadeiro`/`falso` ou `"texto"` |
| `carrega <slot>` | empilha o valor do local `slot` do registro de ativação atual |
| `armazena <slot>` | desempilha e guarda no local `slot` |
| `soma` `subtrai` `multiplica` | desempilha `b`, `a`; empilha `a op b` (`soma` também concatena textos) |
| `divide` | desempilha `b`, `a`; empilha `a / b` (inteiros: truncado para zero). `b = 0` → erro de execução |
| `resto` | desempilha `b`, `a`; empilha o resto com o sinal de `a`. `b = 0` → erro de execução |
| `igual` `diferente` `menor` `menor_igual` `maior` `maior_igual` | desempilha `b`, `a`; empilha o `logico` da comparação |
| `e` `ou` | desempilha `b`, `a`; empilha o resultado (os dois lados já foram avaliados) |
| `nao` | desempilha `a`; empilha `nao a` |
| `nega` | desempilha `a`; empilha `-a` |
| `para_real` | desempilha um inteiro; empilha o mesmo valor como real |
| `desvia <L>` | salta para o rótulo `L` |
| `desvia_se_falso <L>` | desempilha; se for `falso`, salta para `L` |
| `chama <f> <n>` | desempilha `n` argumentos para os primeiros slots de um **novo registro de ativação** e começa `f`. Mais de 10000 chamadas aninhadas → erro de execução (estouro de pilha) |
| `retorna` | destrói o registro de ativação atual e volta para quem chamou |
| `retorna_valor` | igual, deixando o topo da pilha como resultado para quem chamou |
| `descarta` | desempilha e joga fora (resultado de chamada usada como comando) |
| `escreve` | desempilha e imprime no formato da seção 4.5, com quebra de linha |
| `linha <L> <C>` | não mexe na pilha: registra a linha do comando atual, para os erros de execução |
| `<L>:` | rótulo (destino de desvio) |

A VM é iterativa: cada chamada empilha um registro de ativação (função, `pc`,
locais, linha atual) numa lista, sem usar a recursão do Python. Cada chamada tem
os seus próprios locais, e é isso que faz a recursão funcionar.

## Programa do grupo

[`exemplos/grupo.mpl`](exemplos/grupo.mpl): Torre de Hanói (recursão com
texto), contagem de movimentos, sequência de Collatz, raiz quadrada por Newton
(reais) e paridade por recursão mútua. Saída esperada em
[`exemplos/grupo.saida`](exemplos/grupo.saida).
