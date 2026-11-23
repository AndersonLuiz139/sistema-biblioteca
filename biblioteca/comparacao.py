from typing import NamedTuple

from .funcoes_puras import (
    VALOR_MULTA_DIARIA,
    calcular_multa,
    gerar_relatorio_de_multas,
)


class ResultadoDaComparacao(NamedTuple):
    total_imperativo: float
    total_funcional: float
    resultados_equivalentes: bool


def calcular_total_das_multas_imperativo(
    emprestimos, data_referencia, valor_multa_diaria=VALOR_MULTA_DIARIA
):
    total = 0.0
    for emprestimo in emprestimos:
        if emprestimo.esta_ativo():
            dias = (data_referencia - emprestimo.data_prevista_devolucao).days
            if dias > 0:
                total = total + dias * valor_multa_diaria
    return round(total, 2)


def calcular_total_das_multas_funcional(
    emprestimos, data_referencia, valor_multa_diaria=VALOR_MULTA_DIARIA
):
    return gerar_relatorio_de_multas(
        emprestimos, data_referencia, valor_multa_diaria
    ).valor_total


def contar_livros_por_categoria_imperativo(livros):
    contagem = {}
    for livro in livros:
        if livro.categoria in contagem:
            contagem[livro.categoria] = contagem[livro.categoria] + 1
        else:
            contagem[livro.categoria] = 1
    return contagem


def comparar_implementacoes(
    emprestimos, data_referencia, valor_multa_diaria=VALOR_MULTA_DIARIA
):
    total_imperativo = calcular_total_das_multas_imperativo(
        emprestimos, data_referencia, valor_multa_diaria
    )
    total_funcional = calcular_total_das_multas_funcional(
        emprestimos, data_referencia, valor_multa_diaria
    )
    return ResultadoDaComparacao(
        total_imperativo=total_imperativo,
        total_funcional=total_funcional,
        resultados_equivalentes=abs(total_imperativo - total_funcional) < 0.001,
    )


def demonstrar_pureza_de_calcular_multa(dias_de_atraso, quantidade_de_chamadas=3):
    return tuple(
        calcular_multa(dias_de_atraso) for _ in range(quantidade_de_chamadas)
    )
