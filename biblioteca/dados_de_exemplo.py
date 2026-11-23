from datetime import date

from .biblioteca import Biblioteca
from .modelos import Livro, Usuario

DATA_DE_REFERENCIA = date(2025, 10, 25)

LIVROS_DE_EXEMPLO = (
    Livro("L001", "Clean Code", "Robert C. Martin", "Engenharia de Software"),
    Livro("L002", "O Programador Pragmatico", "Andrew Hunt", "Engenharia de Software"),
    Livro("L003", "Estruturas de Dados e Algoritmos", "Thomas Cormen", "Algoritmos"),
    Livro("L004", "Introducao a Programacao Funcional", "Richard Bird", "Programacao Funcional"),
    Livro("L005", "Padroes de Projeto", "Erich Gamma", "Engenharia de Software"),
    Livro("L006", "Algoritmos: Teoria e Pratica", "Thomas Cormen", "Algoritmos"),
    Livro("L007", "Programacao Funcional em Python", "David Mertz", "Programacao Funcional"),
    Livro("L008", "Sistemas de Banco de Dados", "Ramez Elmasri", "Banco de Dados"),
)

USUARIOS_DE_EXEMPLO = (
    Usuario("U001", "Ana Carolina Souza", "2023001"),
    Usuario("U002", "Bruno Henrique Lima", "2023002"),
    Usuario("U003", "Carla Mendes Ribeiro", "2023003"),
    Usuario("U004", "Diego Alves Ferreira", "2023004"),
)

EMPRESTIMOS_DE_EXEMPLO = (
    ("EMP0001", "L001", "U001", date(2025, 10, 1), 14, None),
    ("EMP0002", "L002", "U002", date(2025, 10, 5), 14, None),
    ("EMP0003", "L003", "U001", date(2025, 10, 18), 14, None),
    ("EMP0004", "L004", "U003", date(2025, 9, 20), 14, date(2025, 10, 20)),
    ("EMP0005", "L005", "U002", date(2025, 10, 20), 7, None),
    ("EMP0006", "L006", "U004", date(2025, 9, 15), 14, None),
)


def montar_biblioteca_de_exemplo(nome="Biblioteca Universitaria Central"):
    biblioteca = Biblioteca(nome)

    for livro in LIVROS_DE_EXEMPLO:
        biblioteca.cadastrar_livro(livro)

    for usuario in USUARIOS_DE_EXEMPLO:
        biblioteca.cadastrar_usuario(usuario)

    for identificador, livro, usuario, data_emprestimo, prazo, devolucao in EMPRESTIMOS_DE_EXEMPLO:
        biblioteca.registrar_emprestimo(
            livro,
            usuario,
            data_emprestimo=data_emprestimo,
            dias_de_prazo=prazo,
            identificador=identificador,
        )
        if devolucao is not None:
            biblioteca.registrar_devolucao(identificador, devolucao)

    return biblioteca
