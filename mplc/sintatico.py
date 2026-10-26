"""
Entrega 2 — analise sintatica.

Transformar a lista de tokens numa arvore.

Sugestao forte: descida recursiva, uma funcao por nivel de precedencia, na
ordem da secao 3.3 da especificacao. E como voces vao enxergar a precedencia
virar formato de arvore.

Gerador de parser (ANTLR, PLY, yacc) esta proibido nesta entrega e na
anterior — o objetivo e entender, e o gerador esconde exatamente a parte
que esta sendo ensinada.

Leiam antes: LINGUAGEM.md secoes 3 a 5, e CONTRATOS.md secao 3.
"""
from mplc.erros import ErroMPL


class No:
    """Um no da arvore. O rotulo e o que sai no --ast."""

    def __init__(self, rotulo, filhos=None, linha=0, coluna=0, **extra):
        self.rotulo = rotulo      # 'binario +', 'literal inteiro 1', 'bloco', ...
        self.filhos = filhos or []
        self.linha = linha
        self.coluna = coluna
        self.extra = extra        # o que a semantica quiser pendurar depois

    @property
    def tipo_no(self):
        return self.extra['no']


TIPOS_VARIAVEL = {'TIPO_INTEIRO': 'inteiro', 'TIPO_REAL': 'real',
                  'TIPO_LOGICO': 'logico', 'TIPO_TEXTO': 'texto'}
TIPOS_RETORNO = dict(TIPOS_VARIAVEL, TIPO_VAZIO='vazio')

# Um nivel por linha da secao 3.3, do mais fraco para o mais forte.
# Cada nivel binario e associativo a esquerda.
NIVEIS = [
    {'OU'},
    {'E'},
    {'IGUAL', 'DIFERENTE'},
    {'MENOR', 'MENOR_IGUAL', 'MAIOR', 'MAIOR_IGUAL'},
    {'MAIS', 'MENOS'},
    {'VEZES', 'DIVIDE', 'RESTO'},
]

NOMES = {
    'ID': 'um nome', 'PONTO_VIRGULA': "';'", 'ABRE_PAR': "'('", 'FECHA_PAR': "')'",
    'ABRE_CHAVE': "'{'", 'FECHA_CHAVE': "'}'", 'ATRIBUI': "'='", 'FIM_ARQUIVO': 'o fim do arquivo',
}


def formata_real(lexema):
    return f'{float(lexema):.6f}'


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    # --- utilitarios -------------------------------------------------------

    @property
    def atual(self):
        return self.tokens[self.i]

    def ve(self, *tipos):
        return self.atual.tipo in tipos

    def erro(self, esperado):
        t = self.atual
        visto = 'o fim do arquivo' if t.tipo == 'FIM_ARQUIVO' else f"'{t.lexema}'"
        raise ErroMPL('sintatico', t.linha, t.coluna, f'esperava {esperado}, encontrei {visto}')

    def consome(self, tipo, esperado=None):
        if self.atual.tipo != tipo:
            self.erro(esperado or NOMES.get(tipo, tipo))
        t = self.atual
        self.i += 1
        return t

    # --- programa e funcoes --------------------------------------------------

    def programa(self):
        funcoes = []
        while not self.ve('FIM_ARQUIVO'):
            funcoes.append(self.funcao())
        return No('programa', funcoes, 1, 1, no='programa')

    def funcao(self):
        inicio = self.consome('FUNCAO', "'funcao'")
        if self.atual.tipo not in TIPOS_RETORNO:
            self.erro('o tipo de retorno')
        tipo = TIPOS_RETORNO[self.atual.tipo]
        self.i += 1
        nome = self.consome('ID').lexema
        self.consome('ABRE_PAR')
        params = []
        if not self.ve('FECHA_PAR'):
            params.append(self.parametro())
            while self.ve('VIRGULA'):
                self.i += 1
                params.append(self.parametro())
        self.consome('FECHA_PAR')
        corpo = self.bloco()
        lista = No('parametros', params, inicio.linha, inicio.coluna, no='parametros')
        return No(f'funcao {nome} {tipo}', [lista, corpo], inicio.linha, inicio.coluna,
                  no='funcao', nome=nome, tipo=tipo)

    def parametro(self):
        t = self.atual
        if t.tipo not in TIPOS_VARIAVEL:
            self.erro('o tipo do parametro')
        self.i += 1
        nome = self.consome('ID').lexema
        tipo = TIPOS_VARIAVEL[t.tipo]
        return No(f'parametro {nome} {tipo}', [], t.linha, t.coluna, no='parametro', nome=nome, tipo=tipo)

    # --- comandos -------------------------------------------------------------

    def bloco(self):
        abre = self.consome('ABRE_CHAVE')
        comandos = []
        while not self.ve('FECHA_CHAVE'):
            if self.ve('FIM_ARQUIVO'):
                self.erro("'}'")
            comandos.append(self.comando())
        self.consome('FECHA_CHAVE')
        return No('bloco', comandos, abre.linha, abre.coluna, no='bloco')

    def comando(self):
        t = self.atual
        if t.tipo in TIPOS_VARIAVEL:
            return self.declaracao()
        if t.tipo == 'ID':
            if self.tokens[self.i + 1].tipo == 'ABRE_PAR':
                chamada = self.chamada()
                self.consome('PONTO_VIRGULA')
                return chamada
            self.i += 1
            self.consome('ATRIBUI')
            expr = self.expressao()
            self.consome('PONTO_VIRGULA')
            return No(f'atribuicao {t.lexema}', [expr], t.linha, t.coluna, no='atribuicao', nome=t.lexema)
        if t.tipo == 'SE':
            self.i += 1
            self.consome('ABRE_PAR')
            cond = self.expressao()
            self.consome('FECHA_PAR')
            filhos = [cond, self.bloco()]
            if self.ve('SENAO'):
                self.i += 1
                filhos.append(self.bloco())
            return No('se', filhos, t.linha, t.coluna, no='se')
        if t.tipo == 'ENQUANTO':
            self.i += 1
            self.consome('ABRE_PAR')
            cond = self.expressao()
            self.consome('FECHA_PAR')
            return No('enquanto', [cond, self.bloco()], t.linha, t.coluna, no='enquanto')
        if t.tipo == 'ESCREVA':
            self.i += 1
            self.consome('ABRE_PAR')
            expr = self.expressao()
            self.consome('FECHA_PAR')
            self.consome('PONTO_VIRGULA')
            return No('escreva', [expr], t.linha, t.coluna, no='escreva')
        if t.tipo == 'RETORNE':
            self.i += 1
            filhos = []
            if not self.ve('PONTO_VIRGULA'):
                filhos.append(self.expressao())
            self.consome('PONTO_VIRGULA')
            return No('retorne', filhos, t.linha, t.coluna, no='retorne')
        if t.tipo == 'ABRE_CHAVE':
            return self.bloco()
        self.erro('um comando')

    def declaracao(self):
        t = self.atual
        tipo = TIPOS_VARIAVEL[t.tipo]
        self.i += 1
        nome = self.consome('ID').lexema
        filhos = []
        if self.ve('ATRIBUI'):
            self.i += 1
            filhos.append(self.expressao())
        self.consome('PONTO_VIRGULA')
        return No(f'declaracao {nome} {tipo}', filhos, t.linha, t.coluna,
                  no='declaracao', nome=nome, tipo=tipo)

    # --- expressoes: um nivel de precedencia por funcao -----------------------

    def expressao(self):
        return self.binario(0)

    def binario(self, nivel):
        if nivel == len(NIVEIS):
            return self.unario()
        esq = self.binario(nivel + 1)
        while self.atual.tipo in NIVEIS[nivel]:
            op = self.atual
            self.i += 1
            dir_ = self.binario(nivel + 1)   # o lado direito sobe um nivel: associatividade a esquerda
            esq = No(f'binario {op.lexema}', [esq, dir_], op.linha, op.coluna, no='binario', op=op.lexema)
        return esq

    def unario(self):
        if self.ve('NAO', 'MENOS'):
            op = self.atual
            self.i += 1
            operando = self.unario()         # chama a si mesmo: associatividade a direita
            return No(f'unario {op.lexema}', [operando], op.linha, op.coluna, no='unario', op=op.lexema)
        return self.primario()

    def primario(self):
        t = self.atual
        if t.tipo == 'INTEIRO':
            self.i += 1
            return No(f'literal inteiro {int(t.lexema)}', [], t.linha, t.coluna,
                      no='literal', tipo='inteiro', valor=int(t.lexema))
        if t.tipo == 'REAL':
            self.i += 1
            return No(f'literal real {formata_real(t.lexema)}', [], t.linha, t.coluna,
                      no='literal', tipo='real', valor=float(t.lexema), lexema=t.lexema)
        if t.tipo == 'LOGICO':
            self.i += 1
            return No(f'literal logico {t.lexema}', [], t.linha, t.coluna,
                      no='literal', tipo='logico', valor=(t.lexema == 'verdadeiro'))
        if t.tipo == 'TEXTO':
            self.i += 1
            return No(f'literal texto {t.lexema}', [], t.linha, t.coluna,
                      no='literal', tipo='texto', valor=t.lexema)
        if t.tipo == 'ID':
            if self.tokens[self.i + 1].tipo == 'ABRE_PAR':
                return self.chamada()
            self.i += 1
            return No(f'variavel {t.lexema}', [], t.linha, t.coluna, no='variavel', nome=t.lexema)
        if t.tipo == 'ABRE_PAR':
            self.i += 1
            expr = self.expressao()
            self.consome('FECHA_PAR')
            return expr
        self.erro('uma expressao')

    def chamada(self):
        nome = self.consome('ID')
        self.consome('ABRE_PAR')
        args = []
        if not self.ve('FECHA_PAR'):
            args.append(self.expressao())
            while self.ve('VIRGULA'):
                self.i += 1
                args.append(self.expressao())
        self.consome('FECHA_PAR')
        return No(f'chamada {nome.lexema}', args, nome.linha, nome.coluna, no='chamada', nome=nome.lexema)


def analisar(tokens):
    """Recebe a lista de Token. Devolve a raiz da arvore (um No 'programa')."""
    return Parser(tokens).programa()


def despejar(no, nivel=0, saida=None):
    """Imprime a arvore no formato do --ast. Ja esta pronto: dois espacos por nivel."""
    saida = saida if saida is not None else []
    saida.append('  ' * nivel + no.rotulo)
    for f in no.filhos:
        despejar(f, nivel + 1, saida)
    return saida
