from app.database import engine, Base
from app import models  # important pour que les modèles soient enregistrés

Base.metadata.create_all(bind=engine)
print("Tables created successfully on Neon.")
