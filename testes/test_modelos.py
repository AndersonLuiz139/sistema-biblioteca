import unittest
from datetime import date

from biblioteca.modelos import Emprestimo, Livro, Usuario, criar_emprestimo


class TestLivro(unittest.TestCase):
    def setUp(self):
        self.livro = Livro("L001", "Clean Code", "Robert C. Martin", "Engenharia de Software")

    def test_atributos_sao_expostos_por_propriedades(self):
        self.assertEqual(self.livro.identificador, "L001")
        self.assertEqual(self.livro.titulo, "Clean Code")
        self.assertEqual(self.livro.autor, "Robert C. Martin")
        self.assertEqual(self.livro.categoria, "Engenharia de Software")

    def test_livro_nao_pode_ser_alterado(self):
        with self.assertRaises(AttributeError):
            self.livro.titulo = "Outro titulo"
        with self.assertRaises(AttributeError):
            self.livro._titulo = "Outro titulo"
        self.assertEqual(self.livro.titulo, "Clean Code")

    def test_livro_nao_aceita_campos_vazios(self):
        with self.assertRaises(ValueError):
            Livro("", "Clean Code", "Robert C. Martin", "Engenharia de Software")
        with self.assertRaises(ValueError):
            Livro("L002", "   ", "Robert C. Martin", "Engenharia de Software")

    def test_pertence_a_categoria_ignora_caixa_e_espacos(self):
        self.assertTrue(self.livro.pertence_a_categoria("engenharia de software"))
        self.assertTrue(self.livro.pertence_a_categoria("  ENGENHARIA DE SOFTWARE  "))
        self.assertFalse(self.livro.pertence_a_categoria("Algoritmos"))

    def test_igualdade_por_identificador(self):
        outro = Livro("L001", "Outro titulo", "Outro autor", "Outra categoria")
        self.assertEqual(self.livro, outro)
        self.assertEqual(len({self.livro, outro}), 1)


class TestUsuario(unittest.TestCase):
    def setUp(self):
        self.usuario = Usuario("U001", "Ana Carolina Souza", "2023001")

    def test_atributos_sao_expostos_por_propriedades(self):
        self.assertEqual(self.usuario.identificador, "U001")
        self.assertEqual(self.usuario.nome, "Ana Carolina Souza")
        self.assertEqual(self.usuario.matricula, "2023001")

    def test_usuario_nao_pode_ser_alterado(self):
        with self.assertRaises(AttributeError):
            self.usuario.nome = "Outro nome"
        self.assertEqual(self.usuario.nome, "Ana Carolina Souza")


class TestEmprestimo(unittest.TestCase):
    def setUp(self):
        self.livro = Livro("L001", "Clean Code", "Robert C. Martin", "Engenharia de Software")
        self.usuario = Usuario("U001", "Ana Carolina Souza", "2023001")
        self.emprestimo = Emprestimo(
            "EMP0001",
            self.livro,
            self.usuario,
            date(2025, 10, 1),
            date(2025, 10, 15),
        )

    def test_emprestimo_nasce_ativo(self):
        self.assertTrue(self.emprestimo.esta_ativo())
        self.assertFalse(self.emprestimo.esta_devolvido())
        self.assertIsNone(self.emprestimo.data_devolucao)

    def test_relacionamento_com_livro_e_usuario(self):
        self.assertIs(self.emprestimo.livro, self.livro)
        self.assertIs(self.emprestimo.usuario, self.usuario)

    def test_tipos_invalidos_sao_recusados(self):
        with self.assertRaises(TypeError):
            Emprestimo("EMP0002", "L001", self.usuario, date(2025, 10, 1), date(2025, 10, 15))
        with self.assertRaises(TypeError):
            Emprestimo("EMP0003", self.livro, "U001", date(2025, 10, 1), date(2025, 10, 15))

    def test_data_prevista_anterior_ao_emprestimo_e_recusada(self):
        with self.assertRaises(ValueError):
            Emprestimo(
                "EMP0004", self.livro, self.usuario, date(2025, 10, 15), date(2025, 10, 1)
            )

    def test_dias_de_atraso_sem_atraso_retorna_zero(self):
        self.assertEqual(self.emprestimo.dias_de_atraso(date(2025, 10, 10)), 0)
        self.assertEqual(self.emprestimo.dias_de_atraso(date(2025, 10, 15)), 0)
        self.assertFalse(self.emprestimo.esta_atrasado(date(2025, 10, 15)))

    def test_dias_de_atraso_com_atraso(self):
        self.assertEqual(self.emprestimo.dias_de_atraso(date(2025, 10, 25)), 10)
        self.assertTrue(self.emprestimo.esta_atrasado(date(2025, 10, 25)))

    def test_emprestimo_devolvido_nao_acumula_atraso(self):
        devolvido = self.emprestimo.devolvido_em(date(2025, 10, 20))
        self.assertEqual(devolvido.dias_de_atraso(date(2025, 12, 31)), 0)
        self.assertFalse(devolvido.esta_atrasado(date(2025, 12, 31)))

    def test_devolvido_em_retorna_nova_instancia_sem_alterar_a_original(self):
        devolvido = self.emprestimo.devolvido_em(date(2025, 10, 20))
        self.assertIsNot(devolvido, self.emprestimo)
        self.assertTrue(self.emprestimo.esta_ativo())
        self.assertTrue(devolvido.esta_devolvido())
        self.assertEqual(devolvido.data_devolucao, date(2025, 10, 20))
        self.assertEqual(devolvido.identificador, self.emprestimo.identificador)

    def test_devolver_duas_vezes_e_recusado(self):
        devolvido = self.emprestimo.devolvido_em(date(2025, 10, 20))
        with self.assertRaises(ValueError):
            devolvido.devolvido_em(date(2025, 10, 21))

    def test_emprestimo_nao_pode_ser_alterado(self):
        with self.assertRaises(AttributeError):
            self.emprestimo.data_devolucao = date(2025, 10, 20)

    def test_criar_emprestimo_calcula_data_prevista(self):
        emprestimo = criar_emprestimo(
            "EMP0005", self.livro, self.usuario, date(2025, 10, 1), 14
        )
        self.assertEqual(emprestimo.data_prevista_devolucao, date(2025, 10, 15))

    def test_criar_emprestimo_recusa_prazo_invalido(self):
        with self.assertRaises(ValueError):
            criar_emprestimo("EMP0006", self.livro, self.usuario, date(2025, 10, 1), 0)
        with self.assertRaises(ValueError):
            criar_emprestimo("EMP0007", self.livro, self.usuario, date(2025, 10, 1), -5)


if __name__ == "__main__":
    unittest.main()
