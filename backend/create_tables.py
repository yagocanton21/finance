from backend.database import engine, Base
from backend.models.usuarios import Usuario

Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso!")