import unittest
from datetime import date

from biblioteca.biblioteca import (
    Biblioteca,
    CadastroDuplicado,
    EmprestimoNaoEncontrado,
    LivroIndisponivel,
    LivroNaoEncontrado,
    UsuarioNaoEncontrado,
)
from biblioteca.dados_de_exemplo import DATA_DE_REFERENCIA, montar_biblioteca_de_exemplo
from biblioteca.modelos import Livro, Usuario


class TestCadastros(unittest.TestCase):
    def setUp(self):
        self.biblioteca = Biblioteca("Biblioteca de Teste")
        self.livro = Livro("L001", "Clean Code", "Robert C. Martin", "Engenharia de Software")
        self.usuario = Usuario("U001", "Ana Carolina Souza", "2023001")

    def test_cadastrar_e_consultar_livro(self):
        self.biblioteca.cadastrar_livro(self.livro)
        self.assertEqual(self.biblioteca.buscar_livro("L001"), self.livro)
        self.assertEqual(len(self.biblioteca.livros), 1)

    def test_cadastrar_e_consultar_usuario(self):
        self.biblioteca.cadastrar_usuario(self.usuario)
        self.assertEqual(self.biblioteca.buscar_usuario("U001"), self.usuario)
        self.assertEqual(len(self.biblioteca.usuarios), 1)

    def test_identificador_duplicado_e_recusado(self):
        self.biblioteca.cadastrar_livro(self.livro)
        with self.assertRaises(CadastroDuplicado):
            self.biblioteca.cadastrar_livro(
                Livro("L001", "Outro livro", "Outro autor", "Outra categoria")
            )
        self.biblioteca.cadastrar_usuario(self.usuario)
        with self.assertRaises(CadastroDuplicado):
            self.biblioteca.cadastrar_usuario(Usuario("U001", "Outro nome", "2023999"))

    def test_tipos_invalidos_sao_recusados(self):
        with self.assertRaises(TypeError):
            self.biblioteca.cadastrar_livro("Clean Code")
        with self.assertRaises(TypeError):
            self.biblioteca.cadastrar_usuario("Ana")

    def test_consultas_inexistentes(self):
        with self.assertRaises(LivroNaoEncontrado):
            self.biblioteca.buscar_livro("L999")
        with self.assertRaises(UsuarioNaoEncontrado):
            self.biblioteca.buscar_usuario("U999")
        with self.assertRaises(EmprestimoNaoEncontrado):
            self.biblioteca.buscar_emprestimo("EMP9999")

    def test_colecoes_expostas_sao_copias_imutaveis(self):
        self.biblioteca.cadastrar_livro(self.livro)
        acervo = self.biblioteca.livros
        self.assertIsInstance(acervo, tuple)
        self.biblioteca.cadastrar_livro(
            Livro("L002", "Padroes de Projeto", "Erich Gamma", "Engenharia de Software")
        )
        self.assertEqual(len(acervo), 1)
        self.assertEqual(len(self.biblioteca.livros), 2)


class TestEmprestimosEDevolucoes(unittest.TestCase):
    def setUp(self):
        self.biblioteca = Biblioteca("Biblioteca de Teste")
        self.biblioteca.cadastrar_livro(
            Livro("L001", "Clean Code", "Robert C. Martin", "Engenharia de Software")
        )
        self.biblioteca.cadastrar_livro(
            Livro("L002", "Padroes de Projeto", "Erich Gamma", "Engenharia de Software")
        )
        self.biblioteca.cadastrar_usuario(Usuario("U001", "Ana Carolina Souza", "2023001"))
        self.biblioteca.cadastrar_usuario(Usuario("U002", "Bruno Henrique Lima", "2023002"))

    def test_registrar_emprestimo_torna_o_livro_indisponivel(self):
        self.assertTrue(self.biblioteca.livro_esta_disponivel("L001"))
        emprestimo = self.biblioteca.registrar_emprestimo(
            "L001", "U001", data_emprestimo=date(2025, 10, 1), dias_de_prazo=14
        )
        self.assertFalse(self.biblioteca.livro_esta_disponivel("L001"))
        self.assertEqual(emprestimo.data_prevista_devolucao, date(2025, 10, 15))
        self.assertTrue(emprestimo.esta_ativo())

    def test_livro_emprestado_nao_pode_ser_emprestado_novamente(self):
        self.biblioteca.registrar_emprestimo("L001", "U001", data_emprestimo=date(2025, 10, 1))
        with self.assertRaises(LivroIndisponivel):
            self.biblioteca.registrar_emprestimo(
                "L001", "U002", data_emprestimo=date(2025, 10, 2)
            )

    def test_emprestimo_exige_livro_e_usuario_cadastrados(self):
        with self.assertRaises(LivroNaoEncontrado):
            self.biblioteca.registrar_emprestimo("L999", "U001")
        with self.assertRaises(UsuarioNaoEncontrado):
            self.biblioteca.registrar_emprestimo("L001", "U999")

    def test_um_usuario_pode_ter_varios_emprestimos(self):
        self.biblioteca.registrar_emprestimo("L001", "U001", data_emprestimo=date(2025, 10, 1))
        self.biblioteca.registrar_emprestimo("L002", "U001", data_emprestimo=date(2025, 10, 2))
        self.assertEqual(len(self.biblioteca.consultar_emprestimos_do_usuario("U001")), 2)
        self.assertEqual(len(self.biblioteca.consultar_emprestimos_do_usuario("U002")), 0)

    def test_identificadores_gerados_sao_sequenciais(self):
        primeiro = self.biblioteca.registrar_emprestimo("L001", "U001")
        segundo = self.biblioteca.registrar_emprestimo("L002", "U002")
        self.assertEqual(primeiro.identificador, "EMP0001")
        self.assertEqual(segundo.identificador, "EMP0002")

    def test_devolucao_registra_a_data_e_libera_o_livro(self):
        emprestimo = self.biblioteca.registrar_emprestimo(
            "L001", "U001", data_emprestimo=date(2025, 10, 1)
        )
        devolvido = self.biblioteca.registrar_devolucao(
            emprestimo.identificador, date(2025, 10, 20)
        )
        self.assertEqual(devolvido.data_devolucao, date(2025, 10, 20))
        self.assertTrue(devolvido.esta_devolvido())
        self.assertTrue(self.biblioteca.livro_esta_disponivel("L001"))

    def test_devolucao_substitui_o_emprestimo_sem_mutar_a_instancia_original(self):
        emprestimo = self.biblioteca.registrar_emprestimo(
            "L001", "U001", data_emprestimo=date(2025, 10, 1)
        )
        self.biblioteca.registrar_devolucao(emprestimo.identificador, date(2025, 10, 20))
        self.assertTrue(emprestimo.esta_ativo())
        self.assertTrue(
            self.biblioteca.buscar_emprestimo(emprestimo.identificador).esta_devolvido()
        )

    def test_livro_devolvido_pode_ser_emprestado_a_outro_usuario(self):
        emprestimo = self.biblioteca.registrar_emprestimo(
            "L001", "U001", data_emprestimo=date(2025, 10, 1)
        )
        self.biblioteca.registrar_devolucao(emprestimo.identificador, date(2025, 10, 20))
        novo = self.biblioteca.registrar_emprestimo(
            "L001", "U002", data_emprestimo=date(2025, 10, 21)
        )
        self.assertEqual(novo.usuario.identificador, "U002")
        self.assertEqual(len(self.biblioteca.emprestimos), 2)

    def test_devolver_emprestimo_inexistente(self):
        with self.assertRaises(EmprestimoNaoEncontrado):
            self.biblioteca.registrar_devolucao("EMP9999", date(2025, 10, 20))

    def test_devolver_duas_vezes_e_recusado(self):
        emprestimo = self.biblioteca.registrar_emprestimo(
            "L001", "U001", data_emprestimo=date(2025, 10, 1)
        )
        self.biblioteca.registrar_devolucao(emprestimo.identificador, date(2025, 10, 20))
        with self.assertRaises(ValueError):
            self.biblioteca.registrar_devolucao(emprestimo.identificador, date(2025, 10, 21))

    def test_consultar_livros_disponiveis_e_emprestados(self):
        self.biblioteca.registrar_emprestimo("L001", "U001")
        disponiveis = self.biblioteca.consultar_livros_disponiveis()
        emprestados = self.biblioteca.consultar_livros_emprestados()
        self.assertEqual(tuple(livro.identificador for livro in disponiveis), ("L002",))
        self.assertEqual(tuple(livro.identificador for livro in emprestados), ("L001",))


class TestBibliotecaDeExemplo(unittest.TestCase):
    def setUp(self):
        self.biblioteca = montar_biblioteca_de_exemplo()

    def test_dados_carregados(self):
        self.assertEqual(len(self.biblioteca.livros), 8)
        self.assertEqual(len(self.biblioteca.usuarios), 4)
        self.assertEqual(len(self.biblioteca.emprestimos), 6)

    def test_consulta_por_categoria(self):
        encontrados = self.biblioteca.consultar_livros_por_categoria("Algoritmos")
        self.assertEqual(len(encontrados), 2)

    def test_emprestimos_ativos_e_atrasados(self):
        self.assertEqual(len(self.biblioteca.consultar_emprestimos_ativos()), 5)
        self.assertEqual(
            len(self.biblioteca.consultar_emprestimos_atrasados(DATA_DE_REFERENCIA)), 3
        )

    def test_relatorio_de_multas(self):
        relatorio = self.biblioteca.gerar_relatorio_de_multas(DATA_DE_REFERENCIA)
        self.assertEqual(relatorio.quantidade_de_emprestimos_atrasados, 3)
        self.assertEqual(relatorio.valor_total, 84.0)
        self.assertEqual(relatorio.valor_multa_diaria, 2.0)

    def test_estatisticas(self):
        estatisticas = self.biblioteca.gerar_estatisticas(DATA_DE_REFERENCIA)
        self.assertEqual(
            dict(estatisticas.livros_por_categoria),
            {
                "Algoritmos": 2,
                "Banco de Dados": 1,
                "Engenharia de Software": 3,
                "Programacao Funcional": 2,
            },
        )
        self.assertEqual(estatisticas.quantidade_de_emprestimos_ativos, 5)
        self.assertEqual(estatisticas.quantidade_de_emprestimos_ativos_atrasados, 3)
        self.assertEqual(estatisticas.valor_total_das_multas, 84.0)

    def test_devolucao_reduz_o_total_de_multas(self):
        self.biblioteca.registrar_devolucao("EMP0001", DATA_DE_REFERENCIA)
        relatorio = self.biblioteca.gerar_relatorio_de_multas(DATA_DE_REFERENCIA)
        self.assertEqual(relatorio.valor_total, 64.0)
        self.assertEqual(relatorio.quantidade_de_emprestimos_atrasados, 2)

    def test_gerar_relatorio_nao_altera_o_estado_da_biblioteca(self):
        antes = self.biblioteca.emprestimos
        self.biblioteca.gerar_relatorio_de_multas(DATA_DE_REFERENCIA)
        self.biblioteca.gerar_estatisticas(DATA_DE_REFERENCIA)
        self.assertEqual(antes, self.biblioteca.emprestimos)


if __name__ == "__main__":
    unittest.main()
