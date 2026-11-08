"""Login do RegulaPRO: senhas guardadas como hash, nunca em texto puro.

Para gerar o hash de uma senha nova:
    python -m functions.auth "minha-senha"
"""

import hashlib
import hmac
import os
import sys
from typing import Any, Dict, Mapping, Optional

ALGORITMO = "pbkdf2_sha256"
ITERACOES = 260_000


def gerar_hash(senha: str, iteracoes: int = ITERACOES) -> str:
    """Gera o hash de uma senha no formato pbkdf2_sha256$iteracoes$sal$hash."""
    sal = os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), bytes.fromhex(sal), iteracoes)
    return f"{ALGORITMO}${iteracoes}${sal}${dk.hex()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Confere uma senha digitada contra o hash salvo."""
    try:
        algoritmo, iteracoes, sal, esperado = senha_hash.split("$")
        if algoritmo != ALGORITMO:
            return False
        dk = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), bytes.fromhex(sal), int(iteracoes))
    except (ValueError, AttributeError):
        return False
    return hmac.compare_digest(dk.hex(), esperado)


def carregar_usuarios(fonte: Optional[Mapping[str, Any]]) -> Dict[str, Dict[str, str]]:
    """Lê os usuários da seção [usuarios] dos segredos, ignorando entradas incompletas."""
    usuarios: Dict[str, Dict[str, str]] = {}
    for login, dados in dict(fonte or {}).items():
        dados = dict(dados)
        if dados.get("senha_hash") and dados.get("tipo") in ("admin", "cliente"):
            usuarios[login] = {
                "senha_hash": dados["senha_hash"],
                "tipo": dados["tipo"],
                "nome": dados.get("nome", login),
            }
    return usuarios


def autenticar(usuarios: Mapping[str, Dict[str, str]], login: str, senha: str) -> Optional[Dict[str, str]]:
    """Retorna os dados do usuário se login e senha conferem; senão None."""
    usuario = usuarios.get(login)
    if usuario and verificar_senha(senha, usuario["senha_hash"]):
        return usuario
    return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Uso: python -m functions.auth "senha"')
        sys.exit(1)
    print(gerar_hash(sys.argv[1]))
