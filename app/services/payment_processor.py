import random


def simulate_payment(amount: float, card_type: str) -> dict:
    """
    Simula el procesamiento de un pago.
    En producción, aquí iría la integración con el gateway de pagos.
    """
    # Simular diferentes escenarios
    rand = random.random()
    
    if rand < 0.85:  # 85% aprobados
        return {
            "status": "approved",
            "message": "Pago aprobado exitosamente"
        }
    elif rand < 0.95:  # 10% rechazados
        return {
            "status": "declined",
            "message": "Tarjeta rechazada por fondos insuficientes"
        }
    else:  # 5% error
        return {
            "status": "error",
            "message": "Error de comunicación con el procesador"
        }