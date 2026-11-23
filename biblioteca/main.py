import sys

from .biblioteca import LivroIndisponivel, LivroNaoEncontrado
from .comparacao import comparar_implementacoes, demonstrar_pureza_de_calcular_multa
from .dados_de_exemplo import DATA_DE_REFERENCIA, montar_biblioteca_de_exemplo
from .funcoes_puras import (
    calcular_multa,
    filtrar_livros_por_categoria,
    selecionar_emprestimos_atrasados,
)

LARGURA = 78


def _preparar_saida():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def _titulo(texto):
    print()
    print("=" * LARGURA)
    print(texto.upper().center(LARGURA))
    print("=" * LARGURA)


def _subtitulo(texto):
    print()
    print(texto)
    print("-" * LARGURA)


def _moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _data(valor):
    return valor.strftime("%d/%m/%Y")


def exibir_acervo(biblioteca):
    _subtitulo("Acervo cadastrado")
    for livro in biblioteca.livros:
        situacao = "disponivel" if biblioteca.livro_esta_disponivel(livro.identificador) else "emprestado"
        print(
            f"  {livro.identificador}  {livro.titulo:<40} {livro.categoria:<24} [{situacao}]"
        )


def exibir_usuarios(biblioteca):
    _subtitulo("Usuarios cadastrados")
    for usuario in biblioteca.usuarios:
        quantidade = len(biblioteca.consultar_emprestimos_do_usuario(usuario.identificador))
        print(
            f"  {usuario.identificador}  {usuario.nome:<28} matricula {usuario.matricula}  "
            f"emprestimos: {quantidade}"
        )


def exibir_emprestimos(biblioteca):
    _subtitulo("Emprestimos registrados")
    for emprestimo in biblioteca.emprestimos:
        if emprestimo.esta_devolvido():
            situacao = f"devolvido em {_data(emprestimo.data_devolucao)}"
        elif emprestimo.esta_atrasado(DATA_DE_REFERENCIA):
            situacao = f"ATRASADO ha {emprestimo.dias_de_atraso(DATA_DE_REFERENCIA)} dia(s)"
        else:
            situacao = "ativo, dentro do prazo"
        print(
            f"  {emprestimo.identificador}  {emprestimo.livro.titulo:<40} "
            f"{emprestimo.usuario.nome:<24} prev. {_data(emprestimo.data_prevista_devolucao)}  {situacao}"
        )


def exibir_filtragem_por_categoria(biblioteca, categoria):
    _subtitulo(f"Filtragem funcional de livros da categoria '{categoria}' (filter)")
    acervo_original = biblioteca.livros
    encontrados = filtrar_livros_por_categoria(acervo_original, categoria)
    for livro in encontrados:
        print(f"  {livro.identificador}  {livro.titulo} - {livro.autor}")
    print()
    print(f"  Livros encontrados: {len(encontrados)}")
    print(f"  Tamanho do acervo original apos a filtragem: {len(acervo_original)}")
    print(f"  Colecao original preservada: {acervo_original == biblioteca.livros}")


def exibir_funcao_pura_de_multa(biblioteca):
    _subtitulo("Funcao pura calcular_multa (transparencia referencial)")
    for dias in (0, 1, 5, 10, 26):
        print(f"  calcular_multa({dias:>2}, 2.00) -> {_moeda(calcular_multa(dias))}")
    print()
    print(f"  Tres chamadas seguidas com dias=10: {demonstrar_pureza_de_calcular_multa(10)}")


def exibir_emprestimos_atrasados(biblioteca):
    _subtitulo(f"Emprestimos ativos em atraso em {_data(DATA_DE_REFERENCIA)} (filter)")
    atrasados = selecionar_emprestimos_atrasados(biblioteca.emprestimos, DATA_DE_REFERENCIA)
    for emprestimo in atrasados:
        print(
            f"  {emprestimo.identificador}  {emprestimo.livro.titulo:<40} "
            f"{emprestimo.dias_de_atraso(DATA_DE_REFERENCIA):>3} dia(s) de atraso"
        )
    print()
    print(f"  Total de emprestimos atrasados: {len(atrasados)}")


def exibir_relatorio_de_multas(biblioteca):
    _subtitulo(f"Relatorio de multas em {_data(DATA_DE_REFERENCIA)} (filter + map + reduce)")
    relatorio = biblioteca.gerar_relatorio_de_multas(DATA_DE_REFERENCIA)
    cabecalho = (
        f"  {'EMPRESTIMO':<12}{'LIVRO':<40}{'USUARIO':<24}{'DIAS':>5}{'MULTA':>14}"
    )
    print(cabecalho)
    print("  " + "-" * (len(cabecalho) - 2))
    for item in relatorio.itens:
        print(
            f"  {item.identificador_do_emprestimo:<12}{item.titulo_do_livro:<40}"
            f"{item.nome_do_usuario:<24}{item.dias_de_atraso:>5}{_moeda(item.valor_da_multa):>14}"
        )
    print("  " + "-" * (len(cabecalho) - 2))
    print(
        f"  {'TOTAL':<12}{'':<40}{'':<24}"
        f"{relatorio.quantidade_de_emprestimos_atrasados:>5}{_moeda(relatorio.valor_total):>14}"
    )
    print()
    print(f"  Valor da multa diaria: {_moeda(relatorio.valor_multa_diaria)}")


def exibir_estatisticas(biblioteca):
    _subtitulo(f"Estatisticas em {_data(DATA_DE_REFERENCIA)} (reduce)")
    estatisticas = biblioteca.gerar_estatisticas(DATA_DE_REFERENCIA)

    print("  Quantidade de livros por categoria:")
    for categoria, quantidade in estatisticas.livros_por_categoria.items():
        print(f"    {categoria:<28} {quantidade}")

    print()
    print("  Quantidade de emprestimos por usuario:")
    for usuario, quantidade in estatisticas.emprestimos_por_usuario.items():
        print(f"    {usuario:<28} {quantidade}")

    print()
    print(f"  Emprestimos ativos:              {estatisticas.quantidade_de_emprestimos_ativos}")
    print(
        f"  Emprestimos ativos em atraso:    {estatisticas.quantidade_de_emprestimos_ativos_atrasados}"
    )
    print(f"  Valor total das multas:          {_moeda(estatisticas.valor_total_das_multas)}")


def exibir_comparacao_entre_paradigmas(biblioteca):
    _subtitulo("Comparacao entre paradigmas: total das multas")
    resultado = comparar_implementacoes(biblioteca.emprestimos, DATA_DE_REFERENCIA)
    print(f"  Versao imperativa (laco e acumulador): {_moeda(resultado.total_imperativo)}")
    print(f"  Versao funcional (filter/map/reduce):  {_moeda(resultado.total_funcional)}")
    print(f"  Resultados equivalentes:               {resultado.resultados_equivalentes}")


def exibir_imutabilidade(biblioteca):
    _subtitulo("Demonstracao de imutabilidade das entidades")
    livro = biblioteca.buscar_livro("L001")
    print(f"  Livro original: {livro.titulo}")
    try:
        livro.titulo = "Titulo alterado"
    except AttributeError as erro:
        print(f"  Tentativa de alteracao recusada: {erro}")

    emprestimo = biblioteca.buscar_emprestimo("EMP0003")
    copia_devolvida = emprestimo.devolvido_em(DATA_DE_REFERENCIA)
    print()
    print(f"  Emprestimo original apos devolvido_em: ativo={emprestimo.esta_ativo()}")
    print(f"  Nova instancia retornada:              ativo={copia_devolvida.esta_ativo()}")
    print(f"  Sao objetos diferentes na memoria:     {emprestimo is not copia_devolvida}")


def exibir_operacoes_com_efeito_colateral(biblioteca):
    _subtitulo("Operacoes com efeito colateral na Biblioteca")
    print(f"  Livros disponiveis antes da devolucao: {len(biblioteca.consultar_livros_disponiveis())}")
    biblioteca.registrar_devolucao("EMP0001", DATA_DE_REFERENCIA)
    print(f"  Devolucao de EMP0001 registrada em {_data(DATA_DE_REFERENCIA)}")
    print(f"  Livros disponiveis depois da devolucao: {len(biblioteca.consultar_livros_disponiveis())}")
    print(f"  Livro L001 disponivel novamente: {biblioteca.livro_esta_disponivel('L001')}")

    relatorio = biblioteca.gerar_relatorio_de_multas(DATA_DE_REFERENCIA)
    print()
    print(f"  Novo total de multas apos a devolucao: {_moeda(relatorio.valor_total)}")

    novo_emprestimo = biblioteca.registrar_emprestimo(
        "L001", "U003", data_emprestimo=DATA_DE_REFERENCIA, dias_de_prazo=14
    )
    print(f"  Novo emprestimo registrado: {novo_emprestimo.identificador} para {novo_emprestimo.usuario.nome}")


def exibir_regras_de_negocio(biblioteca):
    _subtitulo("Validacao das regras de negocio")
    try:
        biblioteca.registrar_emprestimo("L002", "U004", data_emprestimo=DATA_DE_REFERENCIA)
    except LivroIndisponivel as erro:
        print(f"  Emprestimo duplicado bloqueado: {erro}")

    try:
        biblioteca.buscar_livro("L999")
    except LivroNaoEncontrado as erro:
        print(f"  Consulta invalida bloqueada:    {erro}")


def executar_demonstracao():
    _preparar_saida()
    biblioteca = montar_biblioteca_de_exemplo()

    _titulo(biblioteca.nome)
    print(f"Data de referencia utilizada na demonstracao: {_data(DATA_DE_REFERENCIA)}")

    _titulo("1. Orientacao a objetos")
    exibir_acervo(biblioteca)
    exibir_usuarios(biblioteca)
    exibir_emprestimos(biblioteca)

    _titulo("2. Programacao funcional")
    exibir_filtragem_por_categoria(biblioteca, "Engenharia de Software")
    exibir_funcao_pura_de_multa(biblioteca)
    exibir_emprestimos_atrasados(biblioteca)
    exibir_relatorio_de_multas(biblioteca)
    exibir_estatisticas(biblioteca)

    _titulo("3. Comparacao entre paradigmas")
    exibir_comparacao_entre_paradigmas(biblioteca)

    _titulo("4. Imutabilidade e efeitos colaterais")
    exibir_imutabilidade(biblioteca)
    exibir_operacoes_com_efeito_colateral(biblioteca)
    exibir_regras_de_negocio(biblioteca)

    print()
    print("=" * LARGURA)
    print("Demonstracao concluida".center(LARGURA))
    print("=" * LARGURA)
    return biblioteca


if __name__ == "__main__":
    executar_demonstracao()
