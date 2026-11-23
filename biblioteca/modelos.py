from datetime import date, timedelta


class EntidadeImutavel:
    __slots__ = ()

    def _definir(self, nome, valor):
        object.__setattr__(self, nome, valor)

    def __setattr__(self, nome, valor):
        raise AttributeError(
            f"{type(self).__name__} e imutavel: o atributo '{nome}' nao pode ser alterado"
        )

    def __delattr__(self, nome):
        raise AttributeError(
            f"{type(self).__name__} e imutavel: o atributo '{nome}' nao pode ser removido"
        )


def _texto_obrigatorio(valor, nome_do_campo):
    if not isinstance(valor, str) or valor.strip() == "":
        raise ValueError(f"O campo '{nome_do_campo}' deve ser um texto nao vazio")
    return valor.strip()


def _data_obrigatoria(valor, nome_do_campo):
    if not isinstance(valor, date):
        raise TypeError(f"O campo '{nome_do_campo}' deve ser uma data")
    return valor


class Livro(EntidadeImutavel):
    __slots__ = ("_identificador", "_titulo", "_autor", "_categoria")

    def __init__(self, identificador, titulo, autor, categoria):
        self._definir("_identificador", _texto_obrigatorio(identificador, "identificador"))
        self._definir("_titulo", _texto_obrigatorio(titulo, "titulo"))
        self._definir("_autor", _texto_obrigatorio(autor, "autor"))
        self._definir("_categoria", _texto_obrigatorio(categoria, "categoria"))

    @property
    def identificador(self):
        return self._identificador

    @property
    def titulo(self):
        return self._titulo

    @property
    def autor(self):
        return self._autor

    @property
    def categoria(self):
        return self._categoria

    def pertence_a_categoria(self, categoria):
        return self._categoria.casefold() == str(categoria).strip().casefold()

    def __eq__(self, outro):
        return isinstance(outro, Livro) and outro.identificador == self._identificador

    def __hash__(self):
        return hash((type(self).__name__, self._identificador))

    def __repr__(self):
        return f"Livro({self._identificador!r}, {self._titulo!r}, {self._autor!r}, {self._categoria!r})"


class Usuario(EntidadeImutavel):
    __slots__ = ("_identificador", "_nome", "_matricula")

    def __init__(self, identificador, nome, matricula):
        self._definir("_identificador", _texto_obrigatorio(identificador, "identificador"))
        self._definir("_nome", _texto_obrigatorio(nome, "nome"))
        self._definir("_matricula", _texto_obrigatorio(matricula, "matricula"))

    @property
    def identificador(self):
        return self._identificador

    @property
    def nome(self):
        return self._nome

    @property
    def matricula(self):
        return self._matricula

    def __eq__(self, outro):
        return isinstance(outro, Usuario) and outro.identificador == self._identificador

    def __hash__(self):
        return hash((type(self).__name__, self._identificador))

    def __repr__(self):
        return f"Usuario({self._identificador!r}, {self._nome!r}, {self._matricula!r})"


class Emprestimo(EntidadeImutavel):
    __slots__ = (
        "_identificador",
        "_livro",
        "_usuario",
        "_data_emprestimo",
        "_data_prevista_devolucao",
        "_data_devolucao",
    )

    def __init__(
        self,
        identificador,
        livro,
        usuario,
        data_emprestimo,
        data_prevista_devolucao,
        data_devolucao=None,
    ):
        if not isinstance(livro, Livro):
            raise TypeError("O emprestimo deve estar associado a um objeto Livro")
        if not isinstance(usuario, Usuario):
            raise TypeError("O emprestimo deve estar associado a um objeto Usuario")

        data_emprestimo = _data_obrigatoria(data_emprestimo, "data_emprestimo")
        data_prevista_devolucao = _data_obrigatoria(
            data_prevista_devolucao, "data_prevista_devolucao"
        )

        if data_prevista_devolucao < data_emprestimo:
            raise ValueError(
                "A data prevista de devolucao nao pode ser anterior a data do emprestimo"
            )

        if data_devolucao is not None:
            data_devolucao = _data_obrigatoria(data_devolucao, "data_devolucao")
            if data_devolucao < data_emprestimo:
                raise ValueError(
                    "A data de devolucao nao pode ser anterior a data do emprestimo"
                )

        self._definir("_identificador", _texto_obrigatorio(identificador, "identificador"))
        self._definir("_livro", livro)
        self._definir("_usuario", usuario)
        self._definir("_data_emprestimo", data_emprestimo)
        self._definir("_data_prevista_devolucao", data_prevista_devolucao)
        self._definir("_data_devolucao", data_devolucao)

    @property
    def identificador(self):
        return self._identificador

    @property
    def livro(self):
        return self._livro

    @property
    def usuario(self):
        return self._usuario

    @property
    def data_emprestimo(self):
        return self._data_emprestimo

    @property
    def data_prevista_devolucao(self):
        return self._data_prevista_devolucao

    @property
    def data_devolucao(self):
        return self._data_devolucao

    def esta_devolvido(self):
        return self._data_devolucao is not None

    def esta_ativo(self):
        return self._data_devolucao is None

    def dias_de_atraso(self, data_referencia):
        _data_obrigatoria(data_referencia, "data_referencia")
        if self.esta_devolvido():
            return 0
        diferenca = (data_referencia - self._data_prevista_devolucao).days
        return diferenca if diferenca > 0 else 0

    def esta_atrasado(self, data_referencia):
        return self.esta_ativo() and self.dias_de_atraso(data_referencia) > 0

    def devolvido_em(self, data_devolucao):
        if self.esta_devolvido():
            raise ValueError(
                f"O emprestimo '{self._identificador}' ja foi devolvido em {self._data_devolucao}"
            )
        return Emprestimo(
            self._identificador,
            self._livro,
            self._usuario,
            self._data_emprestimo,
            self._data_prevista_devolucao,
            data_devolucao,
        )

    def __eq__(self, outro):
        return (
            isinstance(outro, Emprestimo)
            and outro.identificador == self._identificador
            and outro.data_devolucao == self._data_devolucao
        )

    def __hash__(self):
        return hash((type(self).__name__, self._identificador, self._data_devolucao))

    def __repr__(self):
        situacao = "devolvido" if self.esta_devolvido() else "ativo"
        return (
            f"Emprestimo({self._identificador!r}, livro={self._livro.titulo!r}, "
            f"usuario={self._usuario.nome!r}, {situacao})"
        )


def criar_emprestimo(identificador, livro, usuario, data_emprestimo, dias_de_prazo):
    if not isinstance(dias_de_prazo, int) or dias_de_prazo <= 0:
        raise ValueError("O prazo de devolucao deve ser um numero inteiro de dias maior que zero")
    return Emprestimo(
        identificador,
        livro,
        usuario,
        data_emprestimo,
        data_emprestimo + timedelta(days=dias_de_prazo),
    )
