"""
Entrega 4, segunda metade — geracao do codigo executavel.

Traduz o codigo de tres enderecos para o formato que a VM de voces executa.
O formato do .mplb e de voces, com uma exigencia: tem que ser TEXTO legivel.
Na apresentacao a gente vai abrir um .mplb e ler junto.

Leiam antes: CONTRATOS.md secao 6.

A VM e de pilha: cada instrucao de tres enderecos vira "carrega os operandos,
opera, armazena o resultado". Cada nome (parametro, variavel ou temporario)
vira um numero de slot no registro de ativacao da funcao. O conjunto de
instrucoes esta documentado no README.
"""
import re

OPERACOES = {
    '+': 'soma', '-': 'subtrai', '*': 'multiplica', '/': 'divide', '%': 'resto',
    '==': 'igual', '!=': 'diferente', '<': 'menor', '<=': 'menor_igual',
    '>': 'maior', '>=': 'maior_igual', 'e': 'e', 'ou': 'ou',
}
CONSTANTE = re.compile(r'"|[0-9]|verdadeiro$|falso$')


def eh_constante(operando):
    return CONSTANTE.match(operando) is not None


class Traducao:
    def __init__(self, funcao, tipos_retorno):
        self.f = funcao
        self.tipos_retorno = tipos_retorno
        self.slots = {}
        for p in funcao.params:
            self.slot(p)
        self.saida = []

    def slot(self, nome):
        if nome not in self.slots:
            self.slots[nome] = len(self.slots)
        return self.slots[nome]

    def emite(self, texto):
        self.saida.append('  ' + texto)

    def carrega(self, operando):
        if eh_constante(operando):
            self.emite(f'empilha {operando}')
        else:
            self.emite(f'carrega {self.slot(operando)}')

    def armazena(self, nome):
        self.emite(f'armazena {self.slot(nome)}')

    def instr(self, i):
        op = i[0]
        if op == 'linha':
            self.emite(f'linha {i[1]} {i[2]}')
        elif op == 'copia':
            self.carrega(i[2])
            self.armazena(i[1])
        elif op == 'bin':
            self.carrega(i[3])
            self.carrega(i[4])
            self.emite(OPERACOES[i[2]])
            self.armazena(i[1])
        elif op == 'un':
            self.carrega(i[3])
            self.emite('nao' if i[2] == 'nao' else 'nega')
            self.armazena(i[1])
        elif op == 'real':
            self.carrega(i[2])
            self.emite('para_real')
            self.armazena(i[1])
        elif op == 'rotulo':
            self.saida.append(f'{i[1]}:')
        elif op == 'desvie':
            self.emite(f'desvia {i[1]}')
        elif op == 'seFalso':
            self.carrega(i[1])
            self.emite(f'desvia_se_falso {i[2]}')
        elif op == 'param':
            self.carrega(i[1])
        elif op == 'chama':
            self.emite(f'chama {i[2]} {i[3]}')
            if i[1] is not None:
                self.armazena(i[1])
            elif self.tipos_retorno[i[2]] != 'vazio':
                self.emite('descarta')
        elif op == 'retorne':
            if i[1] is None:
                self.emite('retorna')
            else:
                self.carrega(i[1])
                self.emite('retorna_valor')
        elif op == 'escreva':
            self.carrega(i[1])
            self.emite('escreve')

    def traduz(self):
        for i in self.f.instrs:
            self.instr(i)
        cabecalho = [f'funcao {self.f.nome} {len(self.f.params)} {len(self.slots)}']
        cabecalho += [f'  local {n} {nome}' for nome, n in self.slots.items()]
        return cabecalho + self.saida + ['fim']


def gerar(codigo_intermediario):
    """Devolve as linhas do arquivo .mplb."""
    tipos = {f.nome: f.tipo for f in codigo_intermediario}
    linhas = ['mplb 1', '']
    for f in codigo_intermediario:
        linhas += Traducao(f, tipos).traduz()
        linhas.append('')
    return linhas[:-1]
