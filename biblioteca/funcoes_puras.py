from datetime import date
from functools import reduce
from types import MappingProxyType
from typing import NamedTuple, Tuple

VALOR_MULTA_DIARIA = 2.0


class ItemDeMulta(NamedTuple):
    identificador_do_emprestimo: str
    titulo_do_livro: str
    nome_do_usuario: str
    matricula_do_usuario: str
    data_prevista_devolucao: date
    dias_de_atraso: int
    valor_da_multa: float


class RelatorioDeMultas(NamedTuple):
    data_referencia: date
    valor_multa_diaria: float
    itens: Tuple[ItemDeMulta, ...]
    quantidade_de_emprestimos_atrasados: int
    valor_total: float


class Estatisticas(NamedTuple):
    data_referencia: date
    livros_por_categoria: MappingProxyType
    emprestimos_por_usuario: MappingProxyType
    quantidade_de_emprestimos_ativos: int
    quantidade_de_emprestimos_ativos_atrasados: int
    valor_total_das_multas: float


def calcular_multa(dias_de_atraso, valor_multa_diaria=VALOR_MULTA_DIARIA):
    if dias_de_atraso <= 0:
        return 0.0
    return round(dias_de_atraso * valor_multa_diaria, 2)


def calcular_dias_de_atraso(data_prevista_devolucao, data_referencia):
    diferenca = (data_referencia - data_prevista_devolucao).days
    return diferenca if diferenca > 0 else 0


def filtrar_livros_por_categoria(livros, categoria):
    return tuple(filter(lambda livro: livro.pertence_a_categoria(categoria), livros))


def filtrar_livros_por_autor(livros, autor):
    alvo = str(autor).strip().casefold()
    return tuple(filter(lambda livro: livro.autor.casefold() == alvo, livros))


def selecionar_emprestimos_ativos(emprestimos):
    return tuple(filter(lambda emprestimo: emprestimo.esta_ativo(), emprestimos))


def selecionar_emprestimos_atrasados(emprestimos, data_referencia):
    return tuple(
        filter(lambda emprestimo: emprestimo.esta_atrasado(data_referencia), emprestimos)
    )


def selecionar_emprestimos_do_usuario(emprestimos, identificador_do_usuario):
    return tuple(
        filter(
            lambda emprestimo: emprestimo.usuario.identificador == identificador_do_usuario,
            emprestimos,
        )
    )


def montar_item_de_multa(emprestimo, data_referencia, valor_multa_diaria=VALOR_MULTA_DIARIA):
    dias = emprestimo.dias_de_atraso(data_referencia)
    return ItemDeMulta(
        identificador_do_emprestimo=emprestimo.identificador,
        titulo_do_livro=emprestimo.livro.titulo,
        nome_do_usuario=emprestimo.usuario.nome,
        matricula_do_usuario=emprestimo.usuario.matricula,
        data_prevista_devolucao=emprestimo.data_prevista_devolucao,
        dias_de_atraso=dias,
        valor_da_multa=calcular_multa(dias, valor_multa_diaria),
    )


def gerar_relatorio_de_multas(
    emprestimos, data_referencia, valor_multa_diaria=VALOR_MULTA_DIARIA
):
    atrasados = selecionar_emprestimos_atrasados(emprestimos, data_referencia)

    itens = tuple(
        map(
            lambda emprestimo: montar_item_de_multa(
                emprestimo, data_referencia, valor_multa_diaria
            ),
            atrasados,
        )
    )

    valor_total = reduce(
        lambda total, item: round(total + item.valor_da_multa, 2),
        itens,
        0.0,
    )

    return RelatorioDeMultas(
        data_referencia=data_referencia,
        valor_multa_diaria=valor_multa_diaria,
        itens=itens,
        quantidade_de_emprestimos_atrasados=len(itens),
        valor_total=valor_total,
    )


def contar_livros_por_categoria(livros):
    contagem = reduce(
        lambda acumulado, livro: {
            **acumulado,
            livro.categoria: acumulado.get(livro.categoria, 0) + 1,
        },
        livros,
        {},
    )
    return MappingProxyType(dict(sorted(contagem.items())))


def contar_emprestimos_por_usuario(emprestimos):
    contagem = reduce(
        lambda acumulado, emprestimo: {
            **acumulado,
            emprestimo.usuario.nome: acumulado.get(emprestimo.usuario.nome, 0) + 1,
        },
        emprestimos,
        {},
    )
    return MappingProxyType(dict(sorted(contagem.items())))


def contar_emprestimos_ativos(emprestimos):
    return len(selecionar_emprestimos_ativos(emprestimos))


def contar_emprestimos_ativos_atrasados(emprestimos, data_referencia):
    return len(selecionar_emprestimos_atrasados(emprestimos, data_referencia))


def calcular_total_das_multas(
    emprestimos, data_referencia, valor_multa_diaria=VALOR_MULTA_DIARIA
):
    return gerar_relatorio_de_multas(emprestimos, data_referencia, valor_multa_diaria).valor_total


def gerar_estatisticas(
    livros, emprestimos, data_referencia, valor_multa_diaria=VALOR_MULTA_DIARIA
):
    return Estatisticas(
        data_referencia=data_referencia,
        livros_por_categoria=contar_livros_por_categoria(livros),
        emprestimos_por_usuario=contar_emprestimos_por_usuario(emprestimos),
        quantidade_de_emprestimos_ativos=contar_emprestimos_ativos(emprestimos),
        quantidade_de_emprestimos_ativos_atrasados=contar_emprestimos_ativos_atrasados(
            emprestimos, data_referencia
        ),
        valor_total_das_multas=calcular_total_das_multas(
            emprestimos, data_referencia, valor_multa_diaria
        ),
    )


def identificadores_de_livros_emprestados(emprestimos):
    return frozenset(
        map(
            lambda emprestimo: emprestimo.livro.identificador,
            selecionar_emprestimos_ativos(emprestimos),
        )
    )


def selecionar_livros_disponiveis(livros, emprestimos):
    emprestados = identificadores_de_livros_emprestados(emprestimos)
    return tuple(filter(lambda livro: livro.identificador not in emprestados, livros))
