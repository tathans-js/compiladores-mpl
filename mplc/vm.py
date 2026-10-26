"""
Entrega 4, terceira metade (sim, sao tres) — a maquina virtual.

Le o .mplb e executa. Precisa de:
  - uma pilha de operandos;
  - um registro de ativacao por chamada, com os locais e o ponto de volta;
  - deteccao de divisao por zero e de estouro de pilha, com codigo de saida 2.

Essa e a materia da aula 11 virando codigo: sem registro de ativacao, a
recursao nao funciona.

A VM e iterativa: uma chamada da MPL empilha um registro de ativacao numa
lista, e nao uma chamada do Python. Por isso a profundidade de recursao e
controlada aqui, por LIMITE_CHAMADAS, e nao pelo limite do Python.
"""
from mplc.erros import ErroMPL

LIMITE_CHAMADAS = 10000
ESCAPES = {'n': '\n', 't': '\t', '"': '"', '\\': '\\'}


class FuncaoVM:
    def __init__(self, nome, nparams, nlocais):
        self.nome = nome
        self.nparams = nparams
        self.nlocais = nlocais
        self.codigo = []          # lista de (operacao, argumento)
        self.rotulos = {}


class Registro:
    """O registro de ativacao: a funcao, o ponto onde ela esta, os locais dela."""
    __slots__ = ('funcao', 'pc', 'locais', 'linha', 'coluna')

    def __init__(self, funcao, locais):
        self.funcao = funcao
        self.pc = 0
        self.locais = locais
        self.linha = 1
        self.coluna = 1


def decodifica_texto(lexema):
    corpo, saida, i = lexema[1:-1], [], 0
    while i < len(corpo):
        if corpo[i] == '\\':
            saida.append(ESCAPES[corpo[i + 1]])
            i += 2
        else:
            saida.append(corpo[i])
            i += 1
    return ''.join(saida)


def constante(texto):
    if texto.startswith('"'):
        return decodifica_texto(texto)
    if texto == 'verdadeiro':
        return True
    if texto == 'falso':
        return False
    if '.' in texto:
        return float(texto)
    return int(texto)


def carregar(texto_mplb):
    funcoes, atual = {}, None
    for bruta in texto_mplb.split('\n'):
        linha = bruta.strip()
        if not linha or linha.startswith('mplb') or linha.startswith('local '):
            continue
        if linha.endswith(':') and atual is not None:
            atual.rotulos[linha[:-1]] = len(atual.codigo)
            continue
        op, _, arg = linha.partition(' ')
        if op == 'funcao':
            nome, nparams, nlocais = arg.split()
            atual = FuncaoVM(nome, int(nparams), int(nlocais))
            funcoes[nome] = atual
        elif op == 'fim':
            atual = None
        elif op == 'empilha':
            atual.codigo.append((op, constante(arg)))
        elif op in ('carrega', 'armazena'):
            atual.codigo.append((op, int(arg)))
        elif op == 'linha':
            l, c = arg.split()
            atual.codigo.append((op, (int(l), int(c))))
        elif op == 'chama':
            nome, n = arg.split()
            atual.codigo.append((op, (nome, int(n))))
        else:
            atual.codigo.append((op, arg))
    return funcoes


def divisao_inteira(a, b):
    """Truncada em direcao a zero, como em C — o // do Python arredonda para baixo."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def formata(v):
    if isinstance(v, bool):
        return 'verdadeiro' if v else 'falso'
    if isinstance(v, float):
        return f'{v:.6f}'
    return str(v)


def executar(texto_mplb, saida):
    """Executa o bytecode. Escreve o que o programa imprimir em `saida`."""
    funcoes = carregar(texto_mplb)
    principal = funcoes['principal']
    pilha = []
    chamadas = [Registro(principal, [None] * principal.nlocais)]

    def erro(msg):
        r = chamadas[-1]
        raise ErroMPL('execucao', r.linha, r.coluna, msg)

    while chamadas:
        r = chamadas[-1]
        op, arg = r.funcao.codigo[r.pc]
        r.pc += 1

        if op == 'linha':
            r.linha, r.coluna = arg
        elif op == 'empilha':
            pilha.append(arg)
        elif op == 'carrega':
            pilha.append(r.locais[arg])
        elif op == 'armazena':
            r.locais[arg] = pilha.pop()
        elif op == 'desvia':
            r.pc = r.funcao.rotulos[arg]
        elif op == 'desvia_se_falso':
            if not pilha.pop():
                r.pc = r.funcao.rotulos[arg]
        elif op == 'escreve':
            saida.write(formata(pilha.pop()) + '\n')
        elif op == 'descarta':
            pilha.pop()
        elif op == 'nega':
            pilha.append(-pilha.pop())
        elif op == 'nao':
            pilha.append(not pilha.pop())
        elif op == 'para_real':
            pilha.append(float(pilha.pop()))
        elif op == 'chama':
            nome, n = arg
            if len(chamadas) >= LIMITE_CHAMADAS:
                erro(f"estouro de pilha chamando '{nome}'")
            f = funcoes[nome]
            locais = [None] * f.nlocais
            if n:
                locais[:n] = pilha[-n:]
                del pilha[-n:]
            chamadas.append(Registro(f, locais))
        elif op == 'retorna':
            chamadas.pop()
        elif op == 'retorna_valor':
            chamadas.pop()           # o valor fica no topo da pilha para quem chamou
        else:
            b = pilha.pop()
            a = pilha.pop()
            if op == 'soma':
                v = a + b
            elif op == 'subtrai':
                v = a - b
            elif op == 'multiplica':
                v = a * b
            elif op == 'divide':
                if b == 0:
                    erro('divisao por zero')
                v = divisao_inteira(a, b) if isinstance(a, int) else a / b
            elif op == 'resto':
                if b == 0:
                    erro('resto de divisao por zero')
                v = a - b * divisao_inteira(a, b)     # o sinal e o do dividendo
            elif op == 'igual':
                v = a == b
            elif op == 'diferente':
                v = a != b
            elif op == 'menor':
                v = a < b
            elif op == 'menor_igual':
                v = a <= b
            elif op == 'maior':
                v = a > b
            elif op == 'maior_igual':
                v = a >= b
            elif op == 'e':
                v = a and b
            elif op == 'ou':
                v = a or b
            else:
                raise ValueError(f'instrucao desconhecida: {op}')
            pilha.append(v)
