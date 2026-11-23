import unittest
from datetime import date

from biblioteca.funcoes_puras import (
    VALOR_MULTA_DIARIA,
    calcular_dias_de_atraso,
    calcular_multa,
    calcular_total_das_multas,
    contar_emprestimos_ativos,
    contar_emprestimos_ativos_atrasados,
    contar_emprestimos_por_usuario,
    contar_livros_por_categoria,
    filtrar_livros_por_autor,
    filtrar_livros_por_categoria,
    gerar_estatisticas,
    gerar_relatorio_de_multas,
    identificadores_de_livros_emprestados,
    montar_item_de_multa,
    selecionar_emprestimos_ativos,
    selecionar_emprestimos_atrasados,
    selecionar_emprestimos_do_usuario,
    selecionar_livros_disponiveis,
)
from biblioteca.modelos import Emprestimo, Livro, Usuario

DATA_REFERENCIA = date(2025, 10, 25)

LIVROS = (
    Livro("L001", "Clean Code", "Robert C. Martin", "Engenharia de Software"),
    Livro("L002", "O Programador Pragmatico", "Andrew Hunt", "Engenharia de Software"),
    Livro("L003", "Estruturas de Dados", "Thomas Cormen", "Algoritmos"),
    Livro("L004", "Programacao Funcional", "Richard Bird", "Programacao Funcional"),
)

USUARIOS = (
    Usuario("U001", "Ana Carolina Souza", "2023001"),
    Usuario("U002", "Bruno Henrique Lima", "2023002"),
)

EMPRESTIMO_ATRASADO_DEZ_DIAS = Emprestimo(
    "EMP0001", LIVROS[0], USUARIOS[0], date(2025, 10, 1), date(2025, 10, 15)
)
EMPRESTIMO_ATRASADO_SEIS_DIAS = Emprestimo(
    "EMP0002", LIVROS[1], USUARIOS[1], date(2025, 10, 5), date(2025, 10, 19)
)
EMPRESTIMO_NO_PRAZO = Emprestimo(
    "EMP0003", LIVROS[2], USUARIOS[0], date(2025, 10, 18), date(2025, 11, 1)
)
EMPRESTIMO_DEVOLVIDO_COM_ATRASO = Emprestimo(
    "EMP0004",
    LIVROS[3],
    USUARIOS[1],
    date(2025, 9, 20),
    date(2025, 10, 4),
    date(2025, 10, 20),
)

EMPRESTIMOS = (
    EMPRESTIMO_ATRASADO_DEZ_DIAS,
    EMPRESTIMO_ATRASADO_SEIS_DIAS,
    EMPRESTIMO_NO_PRAZO,
    EMPRESTIMO_DEVOLVIDO_COM_ATRASO,
)


class TestCalcularMulta(unittest.TestCase):
    def test_valor_padrao_da_multa_diaria(self):
        self.assertEqual(VALOR_MULTA_DIARIA, 2.0)

    def test_sem_atraso_nao_gera_multa(self):
        self.assertEqual(calcular_multa(0), 0.0)
        self.assertEqual(calcular_multa(-3), 0.0)

    def test_multa_proporcional_aos_dias(self):
        self.assertEqual(calcular_multa(1), 2.0)
        self.assertEqual(calcular_multa(10), 20.0)
        self.assertEqual(calcular_multa(26), 52.0)

    def test_aceita_valor_diario_diferente(self):
        self.assertEqual(calcular_multa(5, 3.5), 17.5)

    def test_transparencia_referencial(self):
        primeira = calcular_multa(7, 2.0)
        segunda = calcular_multa(7, 2.0)
        terceira = calcular_multa(7, 2.0)
        self.assertEqual(primeira, segunda)
        self.assertEqual(segunda, terceira)
        self.assertEqual(primeira, 14.0)

    def test_calcular_dias_de_atraso(self):
        self.assertEqual(calcular_dias_de_atraso(date(2025, 10, 15), date(2025, 10, 25)), 10)
        self.assertEqual(calcular_dias_de_atraso(date(2025, 10, 15), date(2025, 10, 15)), 0)
        self.assertEqual(calcular_dias_de_atraso(date(2025, 10, 15), date(2025, 10, 1)), 0)


class TestFiltragem(unittest.TestCase):
    def test_filtrar_livros_por_categoria(self):
        encontrados = filtrar_livros_por_categoria(LIVROS, "Engenharia de Software")
        self.assertEqual(len(encontrados), 2)
        self.assertEqual(
            tuple(livro.identificador for livro in encontrados), ("L001", "L002")
        )

    def test_filtrar_livros_por_categoria_inexistente(self):
        self.assertEqual(filtrar_livros_por_categoria(LIVROS, "Redes"), ())

    def test_filtragem_nao_altera_a_colecao_original(self):
        acervo = list(LIVROS)
        copia = list(acervo)
        filtrar_livros_por_categoria(acervo, "Algoritmos")
        self.assertEqual(acervo, copia)
        self.assertEqual(len(acervo), 4)

    def test_filtragem_retorna_estrutura_imutavel(self):
        encontrados = filtrar_livros_por_categoria(LIVROS, "Algoritmos")
        self.assertIsInstance(encontrados, tuple)

    def test_filtrar_livros_por_autor(self):
        encontrados = filtrar_livros_por_autor(LIVROS, "thomas cormen")
        self.assertEqual(len(encontrados), 1)
        self.assertEqual(encontrados[0].identificador, "L003")

    def test_selecionar_emprestimos_ativos(self):
        ativos = selecionar_emprestimos_ativos(EMPRESTIMOS)
        self.assertEqual(len(ativos), 3)
        self.assertNotIn(EMPRESTIMO_DEVOLVIDO_COM_ATRASO, ativos)

    def test_selecionar_emprestimos_atrasados(self):
        atrasados = selecionar_emprestimos_atrasados(EMPRESTIMOS, DATA_REFERENCIA)
        self.assertEqual(
            tuple(emprestimo.identificador for emprestimo in atrasados),
            ("EMP0001", "EMP0002"),
        )

    def test_emprestimo_devolvido_nao_entra_nos_atrasados(self):
        atrasados = selecionar_emprestimos_atrasados(EMPRESTIMOS, date(2025, 12, 31))
        self.assertNotIn(EMPRESTIMO_DEVOLVIDO_COM_ATRASO, atrasados)

    def test_selecionar_emprestimos_do_usuario(self):
        da_ana = selecionar_emprestimos_do_usuario(EMPRESTIMOS, "U001")
        self.assertEqual(len(da_ana), 2)

    def test_livros_disponiveis_e_emprestados(self):
        emprestados = identificadores_de_livros_emprestados(EMPRESTIMOS)
        self.assertEqual(emprestados, frozenset({"L001", "L002", "L003"}))
        disponiveis = selecionar_livros_disponiveis(LIVROS, EMPRESTIMOS)
        self.assertEqual(tuple(livro.identificador for livro in disponiveis), ("L004",))


class TestRelatorioDeMultas(unittest.TestCase):
    def setUp(self):
        self.relatorio = gerar_relatorio_de_multas(EMPRESTIMOS, DATA_REFERENCIA)

    def test_quantidade_de_itens(self):
        self.assertEqual(self.relatorio.quantidade_de_emprestimos_atrasados, 2)
        self.assertEqual(len(self.relatorio.itens), 2)

    def test_valor_total(self):
        self.assertEqual(self.relatorio.valor_total, 32.0)

    def test_conteudo_dos_itens(self):
        primeiro = self.relatorio.itens[0]
        self.assertEqual(primeiro.identificador_do_emprestimo, "EMP0001")
        self.assertEqual(primeiro.titulo_do_livro, "Clean Code")
        self.assertEqual(primeiro.nome_do_usuario, "Ana Carolina Souza")
        self.assertEqual(primeiro.dias_de_atraso, 10)
        self.assertEqual(primeiro.valor_da_multa, 20.0)

    def test_relatorio_sem_atrasados(self):
        relatorio = gerar_relatorio_de_multas(EMPRESTIMOS, date(2025, 10, 10))
        self.assertEqual(relatorio.itens, ())
        self.assertEqual(relatorio.valor_total, 0.0)

    def test_relatorio_de_colecao_vazia(self):
        relatorio = gerar_relatorio_de_multas((), DATA_REFERENCIA)
        self.assertEqual(relatorio.valor_total, 0.0)
        self.assertEqual(relatorio.quantidade_de_emprestimos_atrasados, 0)

    def test_relatorio_nao_altera_os_emprestimos_originais(self):
        emprestimos = list(EMPRESTIMOS)
        copia = list(emprestimos)
        gerar_relatorio_de_multas(emprestimos, DATA_REFERENCIA)
        self.assertEqual(emprestimos, copia)
        self.assertTrue(EMPRESTIMO_ATRASADO_DEZ_DIAS.esta_ativo())
        self.assertIsNone(EMPRESTIMO_ATRASADO_DEZ_DIAS.data_devolucao)

    def test_relatorio_e_imutavel(self):
        with self.assertRaises(AttributeError):
            self.relatorio.valor_total = 0.0
        self.assertIsInstance(self.relatorio.itens, tuple)

    def test_relatorio_com_multa_diaria_personalizada(self):
        relatorio = gerar_relatorio_de_multas(EMPRESTIMOS, DATA_REFERENCIA, 1.0)
        self.assertEqual(relatorio.valor_total, 16.0)

    def test_montar_item_de_multa(self):
        item = montar_item_de_multa(EMPRESTIMO_ATRASADO_SEIS_DIAS, DATA_REFERENCIA)
        self.assertEqual(item.dias_de_atraso, 6)
        self.assertEqual(item.valor_da_multa, 12.0)
        self.assertEqual(item.matricula_do_usuario, "2023002")

    def test_calcular_total_das_multas(self):
        self.assertEqual(calcular_total_das_multas(EMPRESTIMOS, DATA_REFERENCIA), 32.0)


class TestEstatisticas(unittest.TestCase):
    def setUp(self):
        self.estatisticas = gerar_estatisticas(LIVROS, EMPRESTIMOS, DATA_REFERENCIA)

    def test_livros_por_categoria(self):
        self.assertEqual(
            dict(self.estatisticas.livros_por_categoria),
            {
                "Algoritmos": 1,
                "Engenharia de Software": 2,
                "Programacao Funcional": 1,
            },
        )

    def test_emprestimos_por_usuario(self):
        self.assertEqual(
            dict(self.estatisticas.emprestimos_por_usuario),
            {"Ana Carolina Souza": 2, "Bruno Henrique Lima": 2},
        )

    def test_contagens_de_emprestimos(self):
        self.assertEqual(self.estatisticas.quantidade_de_emprestimos_ativos, 3)
        self.assertEqual(self.estatisticas.quantidade_de_emprestimos_ativos_atrasados, 2)

    def test_valor_total_das_multas(self):
        self.assertEqual(self.estatisticas.valor_total_das_multas, 32.0)

    def test_mapas_retornados_sao_somente_leitura(self):
        with self.assertRaises(TypeError):
            self.estatisticas.livros_por_categoria["Redes"] = 1
        with self.assertRaises(TypeError):
            self.estatisticas.emprestimos_por_usuario["Carla"] = 1

    def test_contagens_isoladas(self):
        self.assertEqual(contar_emprestimos_ativos(EMPRESTIMOS), 3)
        self.assertEqual(
            contar_emprestimos_ativos_atrasados(EMPRESTIMOS, DATA_REFERENCIA), 2
        )
        self.assertEqual(dict(contar_livros_por_categoria(())), {})
        self.assertEqual(dict(contar_emprestimos_por_usuario(())), {})

    def test_estatisticas_nao_alteram_as_colecoes_originais(self):
        livros = list(LIVROS)
        emprestimos = list(EMPRESTIMOS)
        gerar_estatisticas(livros, emprestimos, DATA_REFERENCIA)
        self.assertEqual(livros, list(LIVROS))
        self.assertEqual(emprestimos, list(EMPRESTIMOS))


if __name__ == "__main__":
    unittest.main()
