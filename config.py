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

# Usuários padrão (em produção, usar banco de dados com hash de senhas)
USUARIOS = {
    "admin": {"senha": "123", "tipo": "admin", "nome": "Administrador"},
    "cliente01": {"senha": "abc", "tipo": "cliente", "nome": "Farmacêutica XPTO"},
    "cliente02": {"senha": "xyz", "tipo": "cliente", "nome": "Laboratório Alfa"},
}
