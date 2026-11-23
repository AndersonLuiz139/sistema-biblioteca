from datetime import date

from .funcoes_puras import (
    VALOR_MULTA_DIARIA,
    filtrar_livros_por_categoria,
    gerar_estatisticas,
    gerar_relatorio_de_multas,
    identificadores_de_livros_emprestados,
    selecionar_emprestimos_ativos,
    selecionar_emprestimos_atrasados,
    selecionar_emprestimos_do_usuario,
    selecionar_livros_disponiveis,
)
from .modelos import Livro, Usuario, criar_emprestimo

PRAZO_PADRAO_EM_DIAS = 14


class LivroNaoEncontrado(Exception):
    pass


class UsuarioNaoEncontrado(Exception):
    pass


class EmprestimoNaoEncontrado(Exception):
    pass


class LivroIndisponivel(Exception):
    pass


class CadastroDuplicado(Exception):
    pass


class Biblioteca:
    def __init__(self, nome, valor_multa_diaria=VALOR_MULTA_DIARIA):
        self._nome = nome
        self._valor_multa_diaria = valor_multa_diaria
        self._livros = {}
        self._usuarios = {}
        self._emprestimos = {}
        self._contador_de_emprestimos = 0

    @property
    def nome(self):
        return self._nome

    @property
    def valor_multa_diaria(self):
        return self._valor_multa_diaria

    @property
    def livros(self):
        return tuple(self._livros.values())

    @property
    def usuarios(self):
        return tuple(self._usuarios.values())

    @property
    def emprestimos(self):
        return tuple(self._emprestimos.values())

    def cadastrar_livro(self, livro):
        if not isinstance(livro, Livro):
            raise TypeError("Apenas objetos Livro podem ser cadastrados no acervo")
        if livro.identificador in self._livros:
            raise CadastroDuplicado(
                f"Ja existe um livro cadastrado com o identificador '{livro.identificador}'"
            )
        self._livros[livro.identificador] = livro
        return livro

    def cadastrar_usuario(self, usuario):
        if not isinstance(usuario, Usuario):
            raise TypeError("Apenas objetos Usuario podem ser cadastrados")
        if usuario.identificador in self._usuarios:
            raise CadastroDuplicado(
                f"Ja existe um usuario cadastrado com o identificador '{usuario.identificador}'"
            )
        self._usuarios[usuario.identificador] = usuario
        return usuario

    def buscar_livro(self, identificador):
        if identificador not in self._livros:
            raise LivroNaoEncontrado(f"Livro '{identificador}' nao encontrado no acervo")
        return self._livros[identificador]

    def buscar_usuario(self, identificador):
        if identificador not in self._usuarios:
            raise UsuarioNaoEncontrado(f"Usuario '{identificador}' nao encontrado")
        return self._usuarios[identificador]

    def buscar_emprestimo(self, identificador):
        if identificador not in self._emprestimos:
            raise EmprestimoNaoEncontrado(f"Emprestimo '{identificador}' nao encontrado")
        return self._emprestimos[identificador]

    def consultar_livros_por_categoria(self, categoria):
        return filtrar_livros_por_categoria(self.livros, categoria)

    def livro_esta_disponivel(self, identificador_do_livro):
        self.buscar_livro(identificador_do_livro)
        return identificador_do_livro not in identificadores_de_livros_emprestados(
            self.emprestimos
        )

    def consultar_livros_disponiveis(self):
        return selecionar_livros_disponiveis(self.livros, self.emprestimos)

    def consultar_livros_emprestados(self):
        emprestados = identificadores_de_livros_emprestados(self.emprestimos)
        return tuple(
            livro for livro in self.livros if livro.identificador in emprestados
        )

    def consultar_emprestimos_ativos(self):
        return selecionar_emprestimos_ativos(self.emprestimos)

    def consultar_emprestimos_atrasados(self, data_referencia):
        return selecionar_emprestimos_atrasados(self.emprestimos, data_referencia)

    def consultar_emprestimos_do_usuario(self, identificador_do_usuario):
        self.buscar_usuario(identificador_do_usuario)
        return selecionar_emprestimos_do_usuario(self.emprestimos, identificador_do_usuario)

    def _proximo_identificador_de_emprestimo(self):
        self._contador_de_emprestimos = self._contador_de_emprestimos + 1
        identificador = f"EMP{self._contador_de_emprestimos:04d}"
        while identificador in self._emprestimos:
            self._contador_de_emprestimos = self._contador_de_emprestimos + 1
            identificador = f"EMP{self._contador_de_emprestimos:04d}"
        return identificador

    def registrar_emprestimo(
        self,
        identificador_do_livro,
        identificador_do_usuario,
        data_emprestimo=None,
        dias_de_prazo=PRAZO_PADRAO_EM_DIAS,
        identificador=None,
    ):
        livro = self.buscar_livro(identificador_do_livro)
        usuario = self.buscar_usuario(identificador_do_usuario)

        if not self.livro_esta_disponivel(identificador_do_livro):
            raise LivroIndisponivel(
                f"O livro '{livro.titulo}' ja esta emprestado para outro usuario"
            )

        data_emprestimo = data_emprestimo or date.today()
        identificador = identificador or self._proximo_identificador_de_emprestimo()

        if identificador in self._emprestimos:
            raise CadastroDuplicado(
                f"Ja existe um emprestimo com o identificador '{identificador}'"
            )

        emprestimo = criar_emprestimo(
            identificador, livro, usuario, data_emprestimo, dias_de_prazo
        )
        self._emprestimos[identificador] = emprestimo
        return emprestimo

    def registrar_devolucao(self, identificador_do_emprestimo, data_devolucao=None):
        emprestimo = self.buscar_emprestimo(identificador_do_emprestimo)
        data_devolucao = data_devolucao or date.today()
        emprestimo_devolvido = emprestimo.devolvido_em(data_devolucao)
        self._emprestimos[identificador_do_emprestimo] = emprestimo_devolvido
        return emprestimo_devolvido

    def gerar_relatorio_de_multas(self, data_referencia):
        return gerar_relatorio_de_multas(
            self.emprestimos, data_referencia, self._valor_multa_diaria
        )

    def gerar_estatisticas(self, data_referencia):
        return gerar_estatisticas(
            self.livros, self.emprestimos, data_referencia, self._valor_multa_diaria
        )

    def __repr__(self):
        return (
            f"Biblioteca({self._nome!r}, livros={len(self._livros)}, "
            f"usuarios={len(self._usuarios)}, emprestimos={len(self._emprestimos)})"
        )
