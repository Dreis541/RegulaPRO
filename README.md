# RegulaPRO 🏢

Sistema de gerenciamento de processos regulatórios ANVISA.

## Estrutura do Projeto

```
RegulaPRO/
├── main.py                    # Ponto de entrada (Streamlit)
├── config.py                  # Configurações globais
├── requirements.txt           # Dependências
├── README.md                  # Este arquivo
├── pages/                     # Páginas da aplicação
│   ├── home.py               # Dashboard principal
│   ├── processos.py          # Listagem e criação de processos
│   ├── acompanhamento.py     # Dashboard de acompanhamento
│   └── relatorios.py         # Geração de relatórios
├── functions/                 # Lógica da aplicação
│   ├── processos.py          # CRUD de processos
│   ├── validacoes.py         # Validações ANVISA
│   ├── database.py           # Operações com banco
│   └── anvisa.py             # Dados e utilitários ANVISA
├── utils/                     # Funções auxiliares
│   ├── formatadores.py       # Formatação de dados
│   ├── helpers.py            # Funções auxiliares
│   └── constantes.py         # Constantes da aplicação
├── data/                      # Banco de dados SQLite (criado automaticamente)
└── tests/                     # Testes automatizados
    ├── conftest.py           # Fixtures do pytest
    ├── test_validacoes.py    # Testes de validações
    ├── test_processos.py     # Testes de processos
    └── test_formatadores.py  # Testes de formatação
```

## Instalação

```bash
pip install -r requirements.txt
```

## Executar

```bash
streamlit run main.py
```

## Testes

```bash
python -m pytest tests/ -v
python -m pytest tests/ --cov=functions --cov=utils  # com cobertura
```

## Usuários padrão

| Usuário    | Senha | Tipo    |
|------------|-------|---------|
| admin      | 123   | admin   |
| cliente01  | abc   | cliente |
| cliente02  | xyz   | cliente |

## Funcionalidades

- **Dashboard**: KPIs, gráficos de status, processos recentes
- **Processos**: CRUD completo com validação de campos e CNPJ
- **Acompanhamento**: Filtros avançados, gráficos, cards de progresso, timeline de eventos
- **Relatórios**: Filtros, métricas resumidas, exportação CSV
- **Documentos**: Upload e download de arquivos
