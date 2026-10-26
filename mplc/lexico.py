"""
Entrega 1 — analise lexica.

Transformar o texto do programa numa lista de tokens.

O que voces tem que devolver: uma lista de Token. O ultimo elemento e sempre
um token FIM_ARQUIVO. A regra de posicao dele esta em CONTRATOS.md, secao 7.

Leiam antes: LINGUAGEM.md secao 2, e CONTRATOS.md secao 2.
"""
from mplc.erros import ErroMPL


class Token:
    __slots__ = ('tipo', 'lexema', 'linha', 'coluna')

    def __init__(self, tipo, lexema, linha, coluna):
        self.tipo = tipo          # 'ID', 'INTEIRO', 'MAIS', ... (a lista esta no contrato)
        self.lexema = lexema      # o texto exato como apareceu no fonte
        self.linha = linha
        self.coluna = coluna      # a coluna do PRIMEIRO caractere do token

    def __str__(self):
        # esta e a linha que o --tokens imprime; nao mexam no formato
        return f"{self.linha},{self.coluna},{self.tipo},{self.lexema}"


RESERVADAS = {
    'funcao': 'FUNCAO', 'retorne': 'RETORNE', 'se': 'SE', 'senao': 'SENAO',
    'enquanto': 'ENQUANTO', 'escreva': 'ESCREVA',
    'inteiro': 'TIPO_INTEIRO', 'real': 'TIPO_REAL', 'logico': 'TIPO_LOGICO',
    'texto': 'TIPO_TEXTO', 'vazio': 'TIPO_VAZIO',
    'verdadeiro': 'LOGICO', 'falso': 'LOGICO',
    'e': 'E', 'ou': 'OU', 'nao': 'NAO',
}

# Os de dois caracteres vem ANTES: '<=' tem que ganhar de '<'.
SIMBOLOS_DUPLOS = {'==': 'IGUAL', '!=': 'DIFERENTE', '<=': 'MENOR_IGUAL', '>=': 'MAIOR_IGUAL'}
SIMBOLOS = {
    '+': 'MAIS', '-': 'MENOS', '*': 'VEZES', '/': 'DIVIDE', '%': 'RESTO',
    '<': 'MENOR', '>': 'MAIOR', '=': 'ATRIBUI',
    '(': 'ABRE_PAR', ')': 'FECHA_PAR', '{': 'ABRE_CHAVE', '}': 'FECHA_CHAVE',
    ',': 'VIRGULA', ';': 'PONTO_VIRGULA',
}
ESCAPES = 'nt"\\'


def eh_letra(c):
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_'


def eh_digito(c):
    return '0' <= c <= '9'


class Lexico:
    def __init__(self, fonte):
        if fonte.startswith('﻿'):
            fonte = fonte[1:]
        self.fonte = fonte
        self.pos = 0
        self.linha = 1
        self.coluna = 1

    def olha(self, k=0):
        i = self.pos + k
        return self.fonte[i] if i < len(self.fonte) else ''

    def avanca(self):
        c = self.fonte[self.pos]
        self.pos += 1
        if c == '\n':
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c

    def erro(self, linha, coluna, msg):
        raise ErroMPL('lexico', linha, coluna, msg)

    def pula_espacos_e_comentarios(self):
        while True:
            c = self.olha()
            if c in (' ', '\t', '\r', '\n') and c != '':
                self.avanca()
            elif c == '/' and self.olha(1) == '/':
                while self.olha() not in ('\n', ''):
                    self.avanca()
            elif c == '/' and self.olha(1) == '*':
                linha, coluna = self.linha, self.coluna
                self.avanca()
                self.avanca()
                while not (self.olha() == '*' and self.olha(1) == '/'):
                    if self.olha() == '':
                        self.erro(linha, coluna, 'comentario de bloco aberto e nunca fechado')
                    self.avanca()
                self.avanca()
                self.avanca()
            else:
                return

    def numero(self, linha, coluna):
        inicio = self.pos
        while eh_digito(self.olha()):
            self.avanca()
        if self.olha() == '.':
            if not eh_digito(self.olha(1)):
                self.erro(self.linha, self.coluna, "numero real sem digito depois do '.'")
            self.avanca()
            while eh_digito(self.olha()):
                self.avanca()
            return Token('REAL', self.fonte[inicio:self.pos], linha, coluna)
        return Token('INTEIRO', self.fonte[inicio:self.pos], linha, coluna)

    def palavra(self, linha, coluna):
        inicio = self.pos
        while eh_letra(self.olha()) or eh_digito(self.olha()):
            self.avanca()
        lexema = self.fonte[inicio:self.pos]
        return Token(RESERVADAS.get(lexema, 'ID'), lexema, linha, coluna)

    def texto(self, linha, coluna):
        inicio = self.pos
        self.avanca()  # a aspa de abertura
        while True:
            c = self.olha()
            if c in ('', '\n'):
                self.erro(linha, coluna, 'texto aberto e nao fechado na mesma linha')
            if c == '"':
                self.avanca()
                return Token('TEXTO', self.fonte[inicio:self.pos], linha, coluna)
            if c == '\\':
                l_barra, c_barra = self.linha, self.coluna
                self.avanca()
                e = self.olha()
                if e in ('', '\n'):
                    self.erro(linha, coluna, 'texto aberto e nao fechado na mesma linha')
                if e not in ESCAPES:
                    self.erro(l_barra, c_barra, f"escape invalido '\\{e}'")
            self.avanca()

    def proximo(self):
        self.pula_espacos_e_comentarios()
        linha, coluna = self.linha, self.coluna
        c = self.olha()
        if c == '':
            return Token('FIM_ARQUIVO', '', linha, coluna)
        if eh_digito(c):
            return self.numero(linha, coluna)
        if eh_letra(c):
            return self.palavra(linha, coluna)
        if c == '"':
            return self.texto(linha, coluna)
        if c == '.':
            self.erro(linha, coluna, "numero real sem digito antes do '.'")
        duplo = c + self.olha(1)
        if duplo in SIMBOLOS_DUPLOS:
            self.avanca()
            self.avanca()
            return Token(SIMBOLOS_DUPLOS[duplo], duplo, linha, coluna)
        if c in SIMBOLOS:
            self.avanca()
            return Token(SIMBOLOS[c], c, linha, coluna)
        self.erro(linha, coluna, f"caractere inesperado '{c}'")


def analisar(fonte):
    """Recebe o texto do programa. Devolve a lista de Token."""
    lex = Lexico(fonte)
    tokens = []
    while True:
        t = lex.proximo()
        tokens.append(t)
        if t.tipo == 'FIM_ARQUIVO':
            return tokens
