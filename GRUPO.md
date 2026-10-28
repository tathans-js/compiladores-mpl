# compilador-mpl

**Turma:** B (segunda)

**Integrantes** (o nome como cada um quer que apareça; sem RA, e-mail ou telefone):

- Jonathans David
- Lucas Soares de Almeida
- Pedro Henrique Teixeira Moroni
- Guilherme de Oliveira Lazari

**Repositório do grupo (com o histórico de commits):** https://github.com/tathans-js/compiladores-mpl

**Linguagem usada no compilador:** Python 3.12

## Como rodar

```bash
./compilar programa.mpl
./executar programa.mplb
```

## O que o grupo quer destacar

A máquina virtual é iterativa: cada chamada cria o seu próprio registro de ativação
numa lista, sem usar a recursão do Python, e é isso que faz a recursão direta e mútua
funcionar e detectar estouro de pilha. No parser, os seis níveis binários de precedência
são uma tabela percorrida por uma única função de descida recursiva.
