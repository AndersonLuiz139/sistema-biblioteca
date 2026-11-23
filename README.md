# Sistema de Gerenciamento de Biblioteca

Projeto da disciplina **Linguagens de Programação** — Atividade Prática de Orientação a Objetos e Programação Funcional.

O sistema gerencia livros, usuários e empréstimos de uma biblioteca universitária, controla a disponibilidade dos exemplares, calcula multas por atraso e gera relatórios e estatísticas. Os dados são mantidos em memória, sem banco de dados.

---

## Integrantes do grupo

| Nome completo                        | Matrícula    |
| ------------------------------------ | ------------ |
| _Anderson Luiz Gomes Soares_         | _(33671338)_ |
| _Leodymann Hugo Silva do Nascimento_ | _(34151303)_ |
| _Ruann Pablo da Silva Pinheiro_      | _(34186077)_ |

---

## Linguagem e requisitos

- **Linguagem:** Python 3 (testado em Python 3.11)
- **Dependências externas:** nenhuma — o projeto usa apenas a biblioteca padrão (`datetime`, `functools.reduce`, `types.MappingProxyType`, `typing.NamedTuple`, `unittest`)
- **Banco de dados:** não utilizado; todos os dados ficam em memória

---

## Como executar

Clone o repositório e entre na pasta do projeto:

```bash
git clone <url-do-repositorio>
cd sistema-biblioteca
```

### Executar a demonstração completa

```bash
python main.py
```

A demonstração cadastra um acervo de exemplo, registra empréstimos e devoluções e imprime, na ordem:

1. Acervo, usuários e empréstimos (orientação a objetos)
2. Filtragem de livros por categoria com `filter`
3. Função pura `calcular_multa` e sua transparência referencial
4. Empréstimos ativos em atraso com `filter`
5. Relatório de multas com `filter` + `map` + `reduce`
6. Estatísticas com `reduce`
7. Comparação entre a versão imperativa e a versão funcional
8. Demonstrações de imutabilidade, efeitos colaterais e regras de negócio

### Executar os testes automatizados

```bash
python -m unittest discover -s testes -t .
```

Saída esperada: `Ran 84 tests ... OK`.

Para ver o nome de cada teste:

```bash
python -m unittest discover -s testes -t . -v
```

---

## Estrutura do projeto

```
sistema-biblioteca/
├── main.py                        ponto de entrada da demonstração
├── README.md
├── biblioteca/
│   ├── __init__.py                exporta a API pública do pacote
│   ├── modelos.py                 Livro, Usuario, Emprestimo (entidades imutáveis)
│   ├── biblioteca.py              classe Biblioteca (operações com efeito colateral)
│   ├── funcoes_puras.py           funções puras, map/filter/reduce, relatórios e estatísticas
│   ├── comparacao.py              versões imperativa e funcional da mesma funcionalidade
│   ├── dados_de_exemplo.py        massa de dados determinística da demonstração
│   └── main.py                    roteiro de exibição da demonstração
├── testes/
│   ├── test_modelos.py            19 testes
│   ├── test_funcoes_puras.py      33 testes
│   ├── test_biblioteca.py         24 testes
    └── test_comparacao.py          8 testes
```

> O código-fonte não contém comentários, conforme exigido pelo enunciado. Toda a documentação está neste README.

---

## Modelagem orientada a objetos

### `Livro`

Representa um exemplar único do acervo.

| Atributo        | Descrição                                     |
| --------------- | --------------------------------------------- |
| `identificador` | código único do livro                         |
| `titulo`        | título da obra                                |
| `autor`         | autor da obra                                 |
| `categoria`     | categoria usada nas filtragens e estatísticas |

Comportamento: `pertence_a_categoria(categoria)`.

### `Usuario`

Representa uma pessoa cadastrada na biblioteca.

| Atributo        | Descrição               |
| --------------- | ----------------------- |
| `identificador` | código único do usuário |
| `nome`          | nome completo           |
| `matricula`     | matrícula institucional |

### `Emprestimo`

Representa a retirada de um livro por um usuário.

| Atributo                  | Descrição                                                           |
| ------------------------- | ------------------------------------------------------------------- |
| `identificador`           | código único do empréstimo                                          |
| `livro`                   | objeto `Livro` associado                                            |
| `usuario`                 | objeto `Usuario` responsável                                        |
| `data_emprestimo`         | data da retirada                                                    |
| `data_prevista_devolucao` | data limite para devolução                                          |
| `data_devolucao`          | data efetiva da devolução, ou `None` quando o empréstimo está ativo |

Comportamento: `esta_ativo()`, `esta_devolvido()`, `dias_de_atraso(data_referencia)`, `esta_atrasado(data_referencia)` e `devolvido_em(data_devolucao)`, que **retorna um novo empréstimo** em vez de alterar o original.

### `Biblioteca`

Gerencia as operações do sistema e é a **única classe com estado mutável**.

- Cadastro e consulta: `cadastrar_livro`, `cadastrar_usuario`, `buscar_livro`, `buscar_usuario`, `buscar_emprestimo`, `consultar_livros_por_categoria`
- Disponibilidade: `livro_esta_disponivel`, `consultar_livros_disponiveis`, `consultar_livros_emprestados`
- Empréstimos e devoluções: `registrar_emprestimo`, `registrar_devolucao`
- Consultas de empréstimos: `consultar_emprestimos_ativos`, `consultar_emprestimos_atrasados`, `consultar_emprestimos_do_usuario`
- Relatórios: `gerar_relatorio_de_multas`, `gerar_estatisticas`

### Relacionamentos e multiplicidades

```
Biblioteca 1 ────── 0..* Livro
Biblioteca 1 ────── 0..* Usuario
Biblioteca 1 ────── 0..* Emprestimo
Usuario    1 ────── 0..* Emprestimo
Livro      1 ────── 0..* Emprestimo      (no máximo 1 empréstimo ativo por livro)
Emprestimo *  ───── 1    Livro
Emprestimo *  ───── 1    Usuario
```

### Encapsulamento

- As entidades guardam os dados em atributos privados (`_titulo`, `_matricula`, `_data_devolucao`, ...) declarados em `__slots__` e expostos apenas por propriedades somente leitura.
- `Livro`, `Usuario` e `Emprestimo` herdam de `EntidadeImutavel`, que sobrescreve `__setattr__` e `__delattr__` para recusar qualquer alteração após a construção.
- As validações ficam dentro dos construtores: texto vazio, tipo errado e data prevista anterior à data do empréstimo são recusados na origem.
- `Biblioteca` mantém os dicionários `_livros`, `_usuarios` e `_emprestimos` privados e devolve **tuplas** nas propriedades `livros`, `usuarios` e `emprestimos`, de modo que nenhum código externo consegue inserir ou remover itens das coleções internas.

---

## Regras de negócio implementadas

| #   | Regra                                                                                                      | Onde está implementada                                              |
| --- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| 1   | Um usuário pode ter vários empréstimos; cada empréstimo tem um único livro e um único usuário              | `Emprestimo.__init__`, `Biblioteca.registrar_emprestimo`            |
| 2   | Um livro não pode estar emprestado para mais de um usuário ao mesmo tempo                                  | `Biblioteca.livro_esta_disponivel` levanta `LivroIndisponivel`      |
| 3   | Cada livro é um exemplar único                                                                             | identificador único no dicionário `_livros`                         |
| 4   | A devolução registra a data e devolve o livro ao acervo disponível                                         | `Biblioteca.registrar_devolucao` + `Emprestimo.devolvido_em`        |
| 5   | Empréstimo atrasado = data prevista ultrapassada **e** livro ainda não devolvido                           | `Emprestimo.esta_atrasado`                                          |
| 6   | Multa de **R$ 2,00 por dia de atraso**; sem atraso não há multa                                            | `VALOR_MULTA_DIARIA` e `calcular_multa`                             |
| 7   | O relatório de multas considera apenas empréstimos ativos e atrasados, em uma data de referência informada | `gerar_relatorio_de_multas(emprestimos, data_referencia)`           |
| 8   | Não há reservas, múltiplos exemplares nem multa para empréstimos já devolvidos                             | `Emprestimo.dias_de_atraso` retorna `0` para empréstimos devolvidos |

O prazo padrão de devolução é de **14 dias** (`PRAZO_PADRAO_EM_DIAS`) e pode ser alterado por empréstimo.

---

## Programação funcional

### Funções puras

Todas as funções de `biblioteca/funcoes_puras.py` são puras: dependem apenas dos parâmetros recebidos, não leem estado global mutável, não gravam nada e não alteram os argumentos.

| Função                                                           | O que faz                                    | Operação funcional          |
| ---------------------------------------------------------------- | -------------------------------------------- | --------------------------- |
| `calcular_multa(dias_de_atraso, valor_multa_diaria)`             | valor da multa a partir dos dias de atraso   | —                           |
| `calcular_dias_de_atraso(data_prevista, data_referencia)`        | dias de atraso, nunca negativo               | —                           |
| `filtrar_livros_por_categoria(livros, categoria)`                | livros de uma categoria                      | `filter`                    |
| `filtrar_livros_por_autor(livros, autor)`                        | livros de um autor                           | `filter`                    |
| `selecionar_emprestimos_ativos(emprestimos)`                     | empréstimos ainda não devolvidos             | `filter`                    |
| `selecionar_emprestimos_atrasados(emprestimos, data_referencia)` | empréstimos ativos em atraso                 | `filter`                    |
| `selecionar_emprestimos_do_usuario(emprestimos, id_usuario)`     | empréstimos de um usuário                    | `filter`                    |
| `montar_item_de_multa(emprestimo, data_referencia, valor)`       | transforma um empréstimo em um item de multa | usada no `map`              |
| `gerar_relatorio_de_multas(emprestimos, data_referencia, valor)` | relatório completo de multas                 | `filter` + `map` + `reduce` |
| `contar_livros_por_categoria(livros)`                            | quantidade de livros por categoria           | `reduce`                    |
| `contar_emprestimos_por_usuario(emprestimos)`                    | quantidade de empréstimos por usuário        | `reduce`                    |
| `contar_emprestimos_ativos(emprestimos)`                         | total de empréstimos ativos                  | `filter`                    |
| `contar_emprestimos_ativos_atrasados(emprestimos, data)`         | total de empréstimos ativos em atraso        | `filter`                    |
| `calcular_total_das_multas(emprestimos, data, valor)`            | soma de todas as multas                      | `reduce`                    |
| `gerar_estatisticas(livros, emprestimos, data, valor)`           | conjunto completo de estatísticas            | `filter` + `reduce`         |
| `identificadores_de_livros_emprestados(emprestimos)`             | códigos dos livros em poder de usuários      | `map` + `filter`            |
| `selecionar_livros_disponiveis(livros, emprestimos)`             | livros livres para empréstimo                | `filter`                    |

### Relatório de multas — `filter` + `map` + `reduce`

O relatório é gerado em três etapas encadeadas, sem nenhum laço:

```python
atrasados = selecionar_emprestimos_atrasados(emprestimos, data_referencia)

itens = tuple(map(
    lambda emprestimo: montar_item_de_multa(emprestimo, data_referencia, valor_multa_diaria),
    atrasados,
))

valor_total = reduce(
    lambda total, item: round(total + item.valor_da_multa, 2),
    itens,
    0.0,
)
```

1. **`filter`** seleciona apenas os empréstimos ativos e em atraso na data de referência.
2. **`map`** transforma cada empréstimo atrasado em um `ItemDeMulta` com os dias de atraso e o valor devido.
3. **`reduce`** agrega os itens em um único valor total.

A data de referência é parâmetro da função e a multa diária é `R$ 2,00` por padrão. Nenhum empréstimo é modificado: o resultado é um `RelatorioDeMultas` novo, imutável.

### Estatísticas com `reduce`

`contar_livros_por_categoria` e `contar_emprestimos_por_usuario` usam `reduce` construindo um dicionário novo a cada passo, em vez de mutar o acumulador:

```python
reduce(
    lambda acumulado, livro: {**acumulado, livro.categoria: acumulado.get(livro.categoria, 0) + 1},
    livros,
    {},
)
```

O resultado é devolvido dentro de um `MappingProxyType`, que é um mapa somente leitura.

### Imutabilidade

- As entidades (`Livro`, `Usuario`, `Emprestimo`) não permitem alteração de atributos: tentar fazê-lo levanta `AttributeError`.
- Devolver um livro não altera o objeto `Emprestimo` existente; `devolvido_em` cria uma nova instância, e a `Biblioteca` substitui a referência no seu dicionário interno.
- Todas as funções de consulta e filtragem retornam **tuplas** ou `frozenset`, nunca listas mutáveis.
- Os relatórios e estatísticas são `NamedTuple` imutáveis (`ItemDeMulta`, `RelatorioDeMultas`, `Estatisticas`).
- Os mapas de contagem são `MappingProxyType`, somente leitura.
- No `reduce`, o acumulador é recriado com `{**acumulado, chave: valor}` em vez de ser mutado.

### Separação entre o puro e o impuro

| Puro (`funcoes_puras.py`, `comparacao.py`, métodos de consulta das entidades) | Impuro (`biblioteca.py`, `dados_de_exemplo.py`, `main.py`)                                |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Recebem dados e devolvem dados novos                                          | Alteram os dicionários internos da `Biblioteca`                                           |
| Mesma entrada → mesma saída, sempre                                           | Resultado depende do estado atual do sistema                                              |
| Não imprimem nem gravam nada                                                  | Imprimem na tela e geram identificadores sequenciais                                      |
| `calcular_multa`, `gerar_relatorio_de_multas`, `gerar_estatisticas`           | `cadastrar_livro`, `registrar_emprestimo`, `registrar_devolucao`, `executar_demonstracao` |

Os métodos `Biblioteca.gerar_relatorio_de_multas` e `Biblioteca.gerar_estatisticas` apenas repassam o estado atual para as funções puras: todo o cálculo acontece fora da classe mutável.

---

## Comparação entre paradigmas

A funcionalidade escolhida foi o **cálculo do valor total das multas**, implementada de duas formas em `biblioteca/comparacao.py`.

### Versão imperativa

```python
total = 0.0
for emprestimo in emprestimos:
    if emprestimo.esta_ativo():
        dias = (data_referencia - emprestimo.data_prevista_devolucao).days
        if dias > 0:
            total = total + dias * valor_multa_diaria
return round(total, 2)
```

### Versão funcional

```python
return gerar_relatorio_de_multas(emprestimos, data_referencia, valor_multa_diaria).valor_total
```

### Resultados

| Aspecto            | Imperativa                                             | Funcional                                                      |
| ------------------ | ------------------------------------------------------ | -------------------------------------------------------------- |
| Estrutura          | um laço com dois `if` aninhados e um acumulador        | três etapas nomeadas: selecionar, transformar, agregar         |
| Legibilidade       | é preciso ler o laço inteiro para entender o resultado | cada etapa tem nome próprio e intenção explícita               |
| Mutabilidade       | a variável `total` muda a cada iteração                | nenhuma variável é reatribuída                                 |
| Reaproveitamento   | o cálculo fica preso dentro do laço                    | `filter`, `map` e `reduce` podem ser reutilizados isoladamente |
| Manutenção         | mudar a regra exige alterar o laço                     | mudar a regra exige alterar apenas a função correspondente     |
| Efeitos colaterais | nenhum, mas o estado interno muda                      | nenhum, e não há estado interno                                |

A função `comparar_implementacoes` executa as duas versões e confirma a equivalência. O teste `test_equivalencia_em_varias_datas_de_referencia` verifica isso para cinco datas de referência diferentes.

---

## Testes automatizados

São 84 testes, organizados em quatro arquivos:

| Arquivo                        | Cobertura                                                                                                                                         |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `testes/test_modelos.py`       | criação e validação das entidades, imutabilidade, cálculo de atraso, devolução que gera nova instância                                            |
| `testes/test_funcoes_puras.py` | cálculo de multas, transparência referencial, filtragens, relatório com `filter`/`map`/`reduce`, estatísticas, preservação das coleções originais |
| `testes/test_biblioteca.py`    | cadastros, duplicidade, empréstimo e devolução, disponibilidade, relatórios da biblioteca de exemplo                                              |
| `testes/test_comparacao.py`    | equivalência entre as versões imperativa e funcional em várias datas                                                                              |

```bash
python -m unittest discover -s testes -t .
```

---

## Dados da demonstração

A demonstração usa a data de referência **25/10/2025** e a seguinte massa de dados:

- 8 livros em 4 categorias (Engenharia de Software: 3, Algoritmos: 2, Programação Funcional: 2, Banco de Dados: 1)
- 4 usuários
- 6 empréstimos: 5 ativos (3 em atraso) e 1 já devolvido

Resultado do relatório de multas em 25/10/2025:

| Empréstimo | Livro                        | Usuário              |    Dias de atraso |        Multa |
| ---------- | ---------------------------- | -------------------- | ----------------: | -----------: |
| EMP0001    | Clean Code                   | Ana Carolina Souza   |                10 |     R$ 20,00 |
| EMP0002    | O Programador Pragmatico     | Bruno Henrique Lima  |                 6 |     R$ 12,00 |
| EMP0006    | Algoritmos: Teoria e Pratica | Diego Alves Ferreira |                26 |     R$ 52,00 |
| **Total**  |                              |                      | **3 empréstimos** | **R$ 84,00** |

O empréstimo EMP0004 foi devolvido com atraso em 20/10/2025 e, conforme a regra 8, **não** entra no relatório de multas.

---

## Entregas individuais

Cada integrante deve entregar, **manuscrito em papel A4 branco sem pauta**, identificado com o nome completo:

1. Diagrama de Classes (UML)
2. Diagrama de Fluxo de Processamento Funcional, representando a geração do relatório de multas
3. Respostas às cinco questões de análise

Os diagramas e as respostas precisam ser escritos à mão por cada aluno, com suas próprias palavras, e representar o código realmente implementado neste repositório.

Além disso, cada integrante responde individualmente a uma pergunta do professor sobre o projeto durante a apresentação.
