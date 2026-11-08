"""Testes do login com senhas em hash."""

from functions.auth import autenticar, carregar_usuarios, gerar_hash, verificar_senha


def test_hash_confere_com_senha_certa():
    h = gerar_hash("segredo", iteracoes=1000)
    assert verificar_senha("segredo", h)
    assert not verificar_senha("errada", h)


def test_hash_nao_guarda_senha_em_texto():
    assert "segredo" not in gerar_hash("segredo", iteracoes=1000)


def test_hash_invalido_nao_quebra():
    assert not verificar_senha("x", "lixo")
    assert not verificar_senha("x", "")


def test_carregar_ignora_usuarios_incompletos():
    fonte = {
        "admin": {"nome": "Adm", "tipo": "admin", "senha_hash": gerar_hash("a", 1000)},
        "sem_hash": {"nome": "X", "tipo": "admin"},
        "tipo_errado": {"tipo": "root", "senha_hash": "h"},
    }
    assert list(carregar_usuarios(fonte)) == ["admin"]
    assert carregar_usuarios(None) == {}


def test_autenticar():
    usuarios = carregar_usuarios({"c1": {"nome": "Cliente", "tipo": "cliente", "senha_hash": gerar_hash("abc", 1000)}})
    assert autenticar(usuarios, "c1", "abc")["nome"] == "Cliente"
    assert autenticar(usuarios, "c1", "xyz") is None
    assert autenticar(usuarios, "ninguem", "abc") is None
