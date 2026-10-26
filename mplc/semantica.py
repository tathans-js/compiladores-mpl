"""
Entrega 3 — analise semantica.

Tabela de simbolos, escopos aninhados e verificacao de tipos.

Tres coisas que costumam ser esquecidas e valem nota:
  - o corpo de uma funcao abre DOIS escopos (o dos parametros e o do bloco);
  - uma funcao pode ser chamada antes de aparecer no arquivo, entao a
    primeira passada so coleta assinaturas;
  - funcao com retorno declarado precisa garantir o retorno em TODOS os
    caminhos.

Leiam antes: LINGUAGEM.md secoes 3 a 5, e CONTRATOS.md secao 4.
"""
import re

from mplc.erros import ErroMPL

NUMERICOS = ('inteiro', 'real')
ARITMETICOS = ('-', '*', '/')
RELACIONAIS = ('<', '<=', '>', '>=')
TEMPORARIO = re.compile(r't[0-9]+')


class Simbolo:
    def __init__(self, nome, categoria, tipo, linha, params=None):
        self.nome = nome
        self.categoria = categoria    # 'funcao', 'parametro' ou 'variavel'
        self.tipo = tipo              # para funcao: o tipo de retorno
        self.linha = linha
        self.params = params or []    # para funcao: os tipos dos parametros
        self.ref = None               # nome unico dentro da funcao (usado pelo codigo intermediario)


class Escopo:
    """Um escopo e um dicionario com um ponteiro para o pai: a busca sobe a cadeia."""

    def __init__(self, numero, descricao, pai):
        self.numero = numero
        self.descricao = descricao
        self.pai = pai
        self.simbolos = {}            # dict guarda a ordem de insercao

    def busca(self, nome):
        e = self
        while e is not None:
            if nome in e.simbolos:
                return e.simbolos[nome]
            e = e.pai
        return None


class Tabela:
    def __init__(self):
        self.escopos = []
        self.global_ = self.abre('global', None)

    def abre(self, descricao, pai):
        e = Escopo(len(self.escopos), descricao, pai)
        self.escopos.append(e)
        return e


def erro(no, msg):
    raise ErroMPL('semantico', no.linha, no.coluna, msg)


def cabe(origem, destino):
    """A unica conversao implicita: inteiro -> real."""
    return origem == destino or (origem == 'inteiro' and destino == 'real')


def converte_se_preciso(no, origem, destino):
    """Marca no no que o valor precisa virar real depois de calculado."""
    if origem == 'inteiro' and destino == 'real':
        no.extra['converte'] = 'real'


class Analisador:
    def __init__(self):
        self.tabela = Tabela()
        self.funcao_atual = None
        self.nomes_usados = None

    # --- passada 1: so as assinaturas -----------------------------------------

    def coleta_assinaturas(self, programa):
        g = self.tabela.global_
        for f in programa.filhos:
            nome = f.extra['nome']
            if nome in g.simbolos:
                erro(f, f"funcao '{nome}' declarada duas vezes")
            params = [p.extra['tipo'] for p in f.filhos[0].filhos]
            g.simbolos[nome] = Simbolo(nome, 'funcao', f.extra['tipo'], f.linha, params)
        principal = g.simbolos.get('principal')
        if principal is None:
            raise ErroMPL('semantico', 1, 1, "falta a funcao 'principal'")
        no = next(f for f in programa.filhos if f.extra['nome'] == 'principal')
        if principal.params:
            erro(no, "'principal' nao pode receber parametros")
        if principal.tipo != 'vazio':
            erro(no, "'principal' tem que devolver vazio")

    # --- passada 2: corpos ------------------------------------------------------

    def programa(self, programa):
        self.coleta_assinaturas(programa)
        for f in programa.filhos:
            self.funcao(f)

    def funcao(self, f):
        self.funcao_atual = f
        self.nomes_usados = {}
        escopo = self.tabela.abre(f"funcao {f.extra['nome']}", self.tabela.global_)
        f.extra['locais'] = []
        for p in f.filhos[0].filhos:
            self.declara(escopo, p, 'parametro')
        self.bloco(f.filhos[1], escopo)
        if f.extra['tipo'] != 'vazio' and not garante_retorno(f.filhos[1]):
            erro(f, f"a funcao '{f.extra['nome']}' nao retorna em todos os caminhos")

    def declara(self, escopo, no, categoria):
        nome = no.extra['nome']
        if nome in escopo.simbolos:
            erro(no, f"'{nome}' ja foi declarado neste escopo")
        s = Simbolo(nome, categoria, no.extra['tipo'], no.linha)
        # nome unico dentro da funcao: o segundo 'x' vira 'x#2', o terceiro 'x#3'...
        n = self.nomes_usados.get(nome, 0) + 1
        self.nomes_usados[nome] = n
        # um nome com cara de temporario (t0, t1...) tambem ganha sufixo, para nao colidir
        s.ref = nome if n == 1 and not TEMPORARIO.fullmatch(nome) else f'{nome}#{n}'
        escopo.simbolos[nome] = s
        no.extra['simbolo'] = s
        self.funcao_atual.extra['locais'].append(s)
        return s

    def bloco(self, b, pai):
        escopo = self.tabela.abre('bloco', pai)
        for c in b.filhos:
            self.comando(c, escopo)

    def comando(self, c, escopo):
        tipo_no = c.tipo_no
        if tipo_no == 'declaracao':
            if c.filhos:
                t = self.expressao(c.filhos[0], escopo)
                if not cabe(t, c.extra['tipo']):
                    erro(c, f"nao da para guardar {t} em '{c.extra['nome']}', que e {c.extra['tipo']}")
                converte_se_preciso(c.filhos[0], t, c.extra['tipo'])
            self.declara(escopo, c, 'variavel')
        elif tipo_no == 'atribuicao':
            s = escopo.busca(c.extra['nome'])
            if s is None:
                erro(c, f"variavel '{c.extra['nome']}' nao declarada")
            c.extra['simbolo'] = s
            t = self.expressao(c.filhos[0], escopo)
            if not cabe(t, s.tipo):
                erro(c, f"nao da para guardar {t} em '{s.nome}', que e {s.tipo}")
            converte_se_preciso(c.filhos[0], t, s.tipo)
        elif tipo_no in ('se', 'enquanto'):
            t = self.expressao(c.filhos[0], escopo)
            if t != 'logico':
                erro(c.filhos[0], f"a condicao do '{tipo_no}' tem que ser logico, veio {t}")
            for b in c.filhos[1:]:
                self.bloco(b, escopo)
        elif tipo_no == 'escreva':
            t = self.expressao(c.filhos[0], escopo)
            if t == 'vazio':
                erro(c.filhos[0], 'escreva nao aceita uma chamada de funcao vazio')
        elif tipo_no == 'retorne':
            esperado = self.funcao_atual.extra['tipo']
            if esperado == 'vazio':
                if c.filhos:
                    erro(c, 'funcao vazio nao retorna valor')
            else:
                if not c.filhos:
                    erro(c, f'falta o valor do retorne: a funcao devolve {esperado}')
                t = self.expressao(c.filhos[0], escopo)
                if not cabe(t, esperado):
                    erro(c, f'a funcao devolve {esperado}, mas o retorne entrega {t}')
                converte_se_preciso(c.filhos[0], t, esperado)
        elif tipo_no == 'chamada':
            self.chamada(c, escopo)
        elif tipo_no == 'bloco':
            self.bloco(c, escopo)

    # --- expressoes: devolvem o tipo, e anotam o no com ele -------------------

    def expressao(self, e, escopo):
        t = self._expressao(e, escopo)
        e.extra['tipo_valor'] = t
        return t

    def _expressao(self, e, escopo):
        tipo_no = e.tipo_no
        if tipo_no == 'literal':
            return e.extra['tipo']
        if tipo_no == 'variavel':
            s = escopo.busca(e.extra['nome'])
            if s is None:
                erro(e, f"variavel '{e.extra['nome']}' nao declarada")
            e.extra['simbolo'] = s
            return s.tipo
        if tipo_no == 'chamada':
            t = self.chamada(e, escopo)
            if t == 'vazio':
                erro(e, f"'{e.extra['nome']}' e vazio e nao pode aparecer numa expressao")
            return t
        if tipo_no == 'unario':
            t = self.expressao(e.filhos[0], escopo)
            if e.extra['op'] == 'nao':
                if t != 'logico':
                    erro(e, f"'nao' exige logico, veio {t}")
                return 'logico'
            if t not in NUMERICOS:
                erro(e, f"'-' unario exige numero, veio {t}")
            return t
        return self.binario(e, escopo)

    def binario(self, e, escopo):
        op = e.extra['op']
        esq, dir_ = e.filhos
        a = self.expressao(esq, escopo)
        b = self.expressao(dir_, escopo)
        numericos = a in NUMERICOS and b in NUMERICOS

        if op in ('e', 'ou'):
            if a != 'logico' or b != 'logico':
                erro(e, f"'{op}' exige logico dos dois lados, veio {a} e {b}")
            return 'logico'
        if op == '%':
            if a != 'inteiro' or b != 'inteiro':
                erro(e, f"'%' so aceita inteiro, veio {a} e {b}")
            return 'inteiro'
        if op == '+' and a == 'texto' and b == 'texto':
            return 'texto'
        if op in ('==', '!=') and not numericos:
            if a != b or a == 'vazio':
                erro(e, f"'{op}' compara dois do mesmo tipo, veio {a} e {b}")
            return 'logico'
        if not numericos:
            erro(e, f"'{op}' exige numeros, veio {a} e {b}")

        # dois numeros: o inteiro sobe para real se o outro lado for real
        comum = 'real' if 'real' in (a, b) else 'inteiro'
        converte_se_preciso(esq, a, comum)
        converte_se_preciso(dir_, b, comum)
        if op in ('+',) + ARITMETICOS:
            return comum
        return 'logico'

    def chamada(self, c, escopo):
        nome = c.extra['nome']
        f = self.tabela.global_.simbolos.get(nome)
        if f is None:
            erro(c, f"funcao '{nome}' nao existe")
        if len(c.filhos) != len(f.params):
            erro(c, f"'{nome}' recebe {len(f.params)} argumento(s), veio {len(c.filhos)}")
        for arg, tp in zip(c.filhos, f.params):
            t = self.expressao(arg, escopo)
            if not cabe(t, tp):
                erro(arg, f"argumento de '{nome}' tem que ser {tp}, veio {t}")
            converte_se_preciso(arg, t, tp)
        c.extra['tipo_retorno'] = f.tipo
        return f.tipo


def garante_retorno(no):
    """Olha a estrutura, nunca o valor das condicoes."""
    tipo_no = no.tipo_no
    if tipo_no == 'retorne':
        return True
    if tipo_no == 'bloco':
        return any(garante_retorno(c) for c in no.filhos)
    if tipo_no == 'se':
        return len(no.filhos) == 3 and garante_retorno(no.filhos[1]) and garante_retorno(no.filhos[2])
    return False


def analisar(arvore):
    """Percorre a arvore, monta a tabela e confere os tipos. Devolve a tabela."""
    a = Analisador()
    a.programa(arvore)
    return a.tabela


def despejar(tabela):
    """Devolve as linhas do --tabela, no formato da secao 4 do contrato."""
    linhas = []
    for e in tabela.escopos:
        if e.pai is None:
            linhas.append(f'escopo {e.numero} global')
        else:
            linhas.append(f'escopo {e.numero} {e.descricao} pai {e.pai.numero}')
        for s in e.simbolos.values():
            if s.categoria == 'funcao':
                linhas.append(f"  {s.nome}|funcao|{s.tipo}({','.join(s.params)})|{s.linha}")
            else:
                linhas.append(f'  {s.nome}|{s.categoria}|{s.tipo}|{s.linha}')
    return linhas
