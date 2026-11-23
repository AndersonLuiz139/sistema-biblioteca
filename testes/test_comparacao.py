import unittest
from datetime import date

from biblioteca.comparacao import (
    calcular_total_das_multas_funcional,
    calcular_total_das_multas_imperativo,
    comparar_implementacoes,
    contar_livros_por_categoria_imperativo,
    demonstrar_pureza_de_calcular_multa,
)
from biblioteca.dados_de_exemplo import DATA_DE_REFERENCIA, montar_biblioteca_de_exemplo
from biblioteca.funcoes_puras import contar_livros_por_categoria


class TestComparacaoEntreParadigmas(unittest.TestCase):
    def setUp(self):
        self.biblioteca = montar_biblioteca_de_exemplo()
        self.emprestimos = self.biblioteca.emprestimos

    def test_as_duas_versoes_produzem_o_mesmo_total(self):
        imperativo = calcular_total_das_multas_imperativo(
            self.emprestimos, DATA_DE_REFERENCIA
        )
        funcional = calcular_total_das_multas_funcional(
            self.emprestimos, DATA_DE_REFERENCIA
        )
        self.assertEqual(imperativo, funcional)
        self.assertEqual(imperativo, 84.0)

    def test_comparacao_reporta_equivalencia(self):
        resultado = comparar_implementacoes(self.emprestimos, DATA_DE_REFERENCIA)
        self.assertTrue(resultado.resultados_equivalentes)
        self.assertEqual(resultado.total_imperativo, resultado.total_funcional)

    def test_equivalencia_em_varias_datas_de_referencia(self):
        for data_referencia in (
            date(2025, 9, 1),
            date(2025, 10, 1),
            date(2025, 10, 25),
            date(2025, 11, 30),
            date(2026, 1, 15),
        ):
            with self.subTest(data_referencia=data_referencia):
                resultado = comparar_implementacoes(self.emprestimos, data_referencia)
                self.assertTrue(resultado.resultados_equivalentes)

    def test_equivalencia_com_colecao_vazia(self):
        resultado = comparar_implementacoes((), DATA_DE_REFERENCIA)
        self.assertEqual(resultado.total_imperativo, 0.0)
        self.assertEqual(resultado.total_funcional, 0.0)

    def test_contagem_por_categoria_nas_duas_versoes(self):
        livros = self.biblioteca.livros
        self.assertEqual(
            contar_livros_por_categoria_imperativo(livros),
            dict(contar_livros_por_categoria(livros)),
        )

    def test_versao_funcional_retorna_estrutura_somente_leitura(self):
        livros = self.biblioteca.livros
        funcional = contar_livros_por_categoria(livros)
        imperativo = contar_livros_por_categoria_imperativo(livros)
        with self.assertRaises(TypeError):
            funcional["Redes"] = 1
        imperativo["Redes"] = 1
        self.assertIn("Redes", imperativo)
        self.assertNotIn("Redes", funcional)

    def test_funcao_pura_devolve_sempre_o_mesmo_valor(self):
        self.assertEqual(demonstrar_pureza_de_calcular_multa(10), (20.0, 20.0, 20.0))
        self.assertEqual(demonstrar_pureza_de_calcular_multa(0), (0.0, 0.0, 0.0))

    def test_nenhuma_das_versoes_altera_os_emprestimos(self):
        antes = self.biblioteca.emprestimos
        calcular_total_das_multas_imperativo(self.emprestimos, DATA_DE_REFERENCIA)
        calcular_total_das_multas_funcional(self.emprestimos, DATA_DE_REFERENCIA)
        self.assertEqual(antes, self.biblioteca.emprestimos)


if __name__ == "__main__":
    unittest.main()
