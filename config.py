"""Configurações globais do RegulaPRO."""

import os

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "processos.db")

# Aplicação
APP_TITLE = "RegulaPRO"
APP_ICON = "🏢"
LAYOUT = "wide"

# Supabase/PostgreSQL: a URL fica em .streamlit/secrets.toml, seção [database].
# Sem ela, o sistema usa o SQLite local em DB_PATH.
DATABASE_URL = None

# Usuários: ficam em .streamlit/secrets.toml (seção [usuarios]), nunca no código.
# Veja .streamlit/secrets.toml.example e functions/auth.py.
