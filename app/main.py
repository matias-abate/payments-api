from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users, cards, payments, transfers

# Crear las tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Payments API",
    description="API de simulación de pagos con tarjeta de crédito y transferencias",
    version="1.0.0"
)

# Registrar routers
app.include_router(users.router)
app.include_router(cards.router)
app.include_router(payments.router)
app.include_router(transfers.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "Payments API funcionando"}