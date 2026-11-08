# RegulaPRO 🏢

Sistema de gerenciamento de processos regulatórios ANVISA.

## Estrutura do Projeto

```
RegulaPRO/
├── main.py                    # Ponto de entrada (Streamlit)
├── config.py                  # Configurações globais
├── requirements.txt           # Dependências
├── README.md                  # Este arquivo
├── telas/                     # Telas da aplicação (não use o nome pages/: o Streamlit cria links automáticos sem login)
│   ├── home.py               # Dashboard principal
│   ├── processos.py          # Listagem e criação de processos
│   ├── acompanhamento.py     # Dashboard de acompanhamento
│   ├── relatorios.py         # Geração de relatórios
│   └── chamados.py           # Chamados de suporte
├── functions/                 # Lógica da aplicação
│   ├── processos.py          # CRUD de processos
│   ├── validacoes.py         # Validações ANVISA
│   ├── database.py           # Operações com banco
│   ├── anvisa.py             # Dados e utilitários ANVISA
│   ├── auth.py               # Login com senha em hash
│   └── tickets.py            # Chamados de suporte
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

## Usuários e senhas

As senhas **não ficam no código**. Elas ficam em `.streamlit/secrets.toml`, que não vai para o Git, guardadas como hash.

1. Copie o modelo:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Gere o hash de cada senha e cole no campo `senha_hash`:
   ```bash
   python -m functions.auth "minha-senha-forte"
   ```
3. No Streamlit Cloud, cole o mesmo conteúdo em **Settings → Secrets**.

Tipos de usuário: `admin` (vê e gerencia tudo) e `cliente` (vê só os próprios chamados).

## Funcionalidades

- **Dashboard**: KPIs, gráficos de status, processos recentes
- **Processos**: CRUD completo com validação de campos e CNPJ
- **Acompanhamento**: Filtros avançados, gráficos, cards de progresso, timeline de eventos
- **Relatórios**: Filtros, métricas resumidas, exportação CSV
- **Documentos**: Upload e download de arquivos
- **Chamados**: clientes abrem e acompanham os próprios chamados; o admin vê todos, atribui técnico, muda status e comenta
