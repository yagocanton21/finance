import bcrypt

# gera criptografia para a senha
def hash_senha(senha: str, rounds: int = 12) -> str:
    """Gera um hash seguro a partir de uma senha em texto puro e retorna como string."""
    salt = bcrypt.gensalt(rounds=rounds)
    hashed_bytes = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')

# verifica se a senha é igual ao hash
def verificar_senha(senha_plana: str, hash_salvo: str) -> bool:
    """Compara uma senha informada com o hash salvo no banco de dados."""
    return bcrypt.checkpw(
        senha_plana.encode('utf-8'),
        hash_salvo.encode('utf-8')
    )
