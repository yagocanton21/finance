from fastapi import FastAPI, HTTPException
from backend.database import engine, SessionLocal, Base
from backend.models import Categoria, Transacao, Usuario
from backend.routers import usuario, login, categorias
# cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# cria aplicação FastAPI
app = FastAPI()

# registra as rotas
app.include_router(usuario.router)
app.include_router(login.router)
app.include_router(categorias.router)


@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao sistema de controle financeiro!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
