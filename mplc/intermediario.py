"""
Entrega 4, primeira metade — codigo de tres enderecos.

A propriedade que define a representacao, e a unica que o verificador mede:
cada linha de operacao tem NO MAXIMO UM OPERADOR. Uma expressao como
a + b * c vira duas linhas, com um temporario no meio.

O formato do despejo e de voces. A propriedade nao e.

Leiam antes: CONTRATOS.md secao 5.

Representacao: cada funcao e uma lista de instrucoes (tuplas). Os operandos
sao texto: um nome de variavel (com '#n' quando o mesmo nome se repete na
funcao), um temporario 'tN', ou uma constante escrita como no fonte
(42, 3.14, verdadeiro, "oi").

  ('linha', L, C)               comeca o comando da linha L do fonte
  ('copia', dst, a)             dst = a
  ('bin', dst, op, a, b)        dst = a op b
  ('un', dst, op, a)            dst = op a           (op e '-' ou 'nao')
  ('real', dst, a)              dst = real a         (inteiro -> real)
  ('rotulo', L)                 L:
  ('desvie', L)                 desvie L
  ('seFalso', a, L)             seFalso a desvie L
  ('param', a)                  empilha um argumento
  ('chama', dst, f, n)          dst = chama f n      (dst None: resultado descartado)
  ('retorne', a)                retorne a            (a None: funcao vazio)
  ('escreva', a)                escreva a
"""

PADRAO = {'inteiro': '0', 'real': '0.0', 'logico': 'falso', 'texto': '""'}


class Funcao:
    def __init__(self, nome, tipo, params, tipos):
        self.nome = nome
        self.tipo = tipo
        self.params = params          # os nomes unicos dos parametros, em ordem
        self.tipos = tipos            # os tipos deles
        self.instrs = []


class Gerador:
    def __init__(self):
        self.funcoes = []
        self.rotulos = 0

    def novo_rotulo(self):
        self.rotulos += 1
        return f'L{self.rotulos - 1}'

    def novo_temp(self):
        self.temps += 1
        return f't{self.temps - 1}'

    def emite(self, *instr):
        self.atual.instrs.append(instr)

    # --- funcoes e comandos -----------------------------------------------------

    def funcao(self, f):
        params = [p.extra['simbolo'] for p in f.filhos[0].filhos]
        self.atual = Funcao(f.extra['nome'], f.extra['tipo'], [s.ref for s in params], [s.tipo for s in params])
        self.temps = 0
        self.funcoes.append(self.atual)
        self.bloco(f.filhos[1])
        if f.extra['tipo'] == 'vazio':
            self.emite('retorne', None)

    def bloco(self, b):
        for c in b.filhos:
            self.comando(c)

    def comando(self, c):
        tipo_no = c.tipo_no
        if tipo_no == 'bloco':
            self.bloco(c)
            return
        if tipo_no != 'enquanto':      # o enquanto marca a linha depois do rotulo, a cada volta
            self.emite('linha', c.linha, c.coluna)
        if tipo_no == 'declaracao':
            s = c.extra['simbolo']
            valor = self.expressao(c.filhos[0]) if c.filhos else PADRAO[s.tipo]
            self.emite('copia', s.ref, valor)
        elif tipo_no == 'atribuicao':
            self.emite('copia', c.extra['simbolo'].ref, self.expressao(c.filhos[0]))
        elif tipo_no == 'escreva':
            self.emite('escreva', self.expressao(c.filhos[0]))
        elif tipo_no == 'retorne':
            self.emite('retorne', self.expressao(c.filhos[0]) if c.filhos else None)
        elif tipo_no == 'chamada':
            self.chamada(c, guarda=False)
        elif tipo_no == 'se':
            cond = self.expressao(c.filhos[0])
            senao = self.novo_rotulo()
            self.emite('seFalso', cond, senao)
            self.bloco(c.filhos[1])
            if len(c.filhos) == 3:
                fim = self.novo_rotulo()
                self.emite('desvie', fim)
                self.emite('rotulo', senao)
                self.bloco(c.filhos[2])
                self.emite('rotulo', fim)
            else:
                self.emite('rotulo', senao)
        elif tipo_no == 'enquanto':
            inicio, fim = self.novo_rotulo(), self.novo_rotulo()
            self.emite('rotulo', inicio)
            self.emite('linha', c.linha, c.coluna)
            cond = self.expressao(c.filhos[0])
            self.emite('seFalso', cond, fim)
            self.bloco(c.filhos[1])
            self.emite('desvie', inicio)
            self.emite('rotulo', fim)

    # --- expressoes: devolvem o operando onde ficou o valor --------------------

    def expressao(self, e):
        r = self._expressao(e)
        if e.extra.get('converte') == 'real':
            t = self.novo_temp()
            self.emite('real', t, r)
            r = t
        return r

    def _expressao(self, e):
        tipo_no = e.tipo_no
        if tipo_no == 'literal':
            tipo, valor = e.extra['tipo'], e.extra['valor']
            if tipo == 'real':
                return e.extra['lexema']
            if tipo == 'logico':
                return 'verdadeiro' if valor else 'falso'
            return str(valor)
        if tipo_no == 'variavel':
            return e.extra['simbolo'].ref
        if tipo_no == 'chamada':
            return self.chamada(e, guarda=True)
        if tipo_no == 'unario':
            a = self.expressao(e.filhos[0])
            t = self.novo_temp()
            self.emite('un', t, e.extra['op'], a)
            return t
        a = self.expressao(e.filhos[0])
        b = self.expressao(e.filhos[1])
        t = self.novo_temp()
        self.emite('bin', t, e.extra['op'], a, b)
        return t

    def chamada(self, c, guarda):
        # os argumentos sao todos calculados antes, para que os 'param' saiam juntos
        args = [self.expressao(a) for a in c.filhos]
        for a in args:
            self.emite('param', a)
        destino = self.novo_temp() if guarda else None
        self.emite('chama', destino, c.extra['nome'], len(args))
        return destino


def gerar(arvore, tabela):
    """Devolve o codigo de tres enderecos."""
    g = Gerador()
    for f in arvore.filhos:
        g.funcao(f)
    return g.funcoes


def despejar_instr(i):
    op = i[0]
    if op == 'linha':
        return f'  # linha {i[1]}'
    if op == 'copia':
        return f'  {i[1]} = {i[2]}'
    if op == 'bin':
        return f'  {i[1]} = {i[3]} {i[2]} {i[4]}'
    if op == 'un':
        return f'  {i[1]} = {i[2]} {i[3]}' if i[2] == 'nao' else f'  {i[1]} = -{i[3]}'
    if op == 'real':
        return f'  {i[1]} = real {i[2]}'
    if op == 'rotulo':
        return f'{i[1]}:'
    if op == 'desvie':
        return f'  desvie {i[1]}'
    if op == 'seFalso':
        return f'  seFalso {i[1]} desvie {i[2]}'
    if op == 'param':
        return f'  param {i[1]}'
    if op == 'chama':
        return f'  {i[1]} = chama {i[2]} {i[3]}' if i[1] else f'  chama {i[2]} {i[3]}'
    if op == 'retorne':
        return f'  retorne {i[1]}' if i[1] is not None else '  retorne'
    if op == 'escreva':
        return f'  escreva {i[1]}'
    raise ValueError(op)


def despejar(codigo):
    """Devolve as linhas do --ir."""
    linhas = []
    for f in codigo:
        params = ', '.join(f'{p} {t}' for p, t in zip(f.params, f.tipos))
        linhas.append(f'funcao {f.nome} {f.tipo} ({params})')
        linhas.extend(despejar_instr(i) for i in f.instrs)
        linhas.append('fim')
        linhas.append('')
    return linhas[:-1]
