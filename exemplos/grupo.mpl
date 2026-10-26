// Programa do grupo: um pouco de matematica em MPL.
// Torre de Hanoi (recursao), Collatz (laco), raiz quadrada por Newton (real)
// e paridade por recursao mutua.

funcao vazio hanoi(inteiro n, texto origem, texto destino, texto auxiliar) {
  se (n == 0) {
    retorne;
  }
  hanoi(n - 1, origem, auxiliar, destino);
  escreva("mova o disco " + "de " + origem + " para " + destino);
  hanoi(n - 1, auxiliar, destino, origem);
}

funcao inteiro movimentos(inteiro n) {
  se (n == 0) {
    retorne 0;
  }
  retorne 2 * movimentos(n - 1) + 1;
}

funcao inteiro collatz(inteiro n) {
  inteiro passos = 0;
  enquanto (n != 1) {
    se (n % 2 == 0) {
      n = n / 2;
    } senao {
      n = 3 * n + 1;
    }
    passos = passos + 1;
  }
  retorne passos;
}

funcao real raiz(real x) {
  real r = x;
  inteiro i = 0;
  enquanto (i < 20) {
    r = (r + x / r) / 2;
    i = i + 1;
  }
  retorne r;
}

funcao logico ehPar(inteiro n) {
  se (n == 0) {
    retorne verdadeiro;
  }
  retorne ehImpar(n - 1);
}

funcao logico ehImpar(inteiro n) {
  se (n == 0) {
    retorne falso;
  }
  retorne ehPar(n - 1);
}

funcao vazio principal() {
  escreva("== Hanoi com 3 discos ==");
  hanoi(3, "A", "C", "B");
  escreva(movimentos(3));
  escreva(movimentos(10));

  escreva("== Collatz ==");
  inteiro n = 1;
  enquanto (n <= 7) {
    escreva(collatz(n));
    n = n + 1;
  }

  escreva("== Raiz quadrada ==");
  escreva(raiz(2));
  escreva(raiz(144.0));

  escreva("== Paridade ==");
  escreva(ehPar(10));
  escreva(ehImpar(7) e nao ehPar(7));
}
