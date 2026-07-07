from ollama import Client
from pydantic import BaseModel

from app.config import settings

# Fixed lista kategorii, trzymana w jednym miejscu (patrz notatka w planie:
# nie pozwalamy modelowi wymyslac nowych nazwy, inaczej sumy przestaja sie
# zgadzac miedzy okresami)
CATEGORIES = [
    "income.salary", "income.bonus", "income.reimbursement",
    "transfers.own", "transfers.family",
    "housing.rent", "housing.utilities", "housing.internet", "housing.insurance",
    "food.groceries", "food.restaurants",
    "transport.fuel", "transport.public_transit", "transport.maintenance",
    "subscriptions.streaming", "subscriptions.software", "subscriptions.gym",
    "shopping.retail", "health.pharmacy", "health.medical",
    "entertainment.leisure", "travel.trips",
    "savings.cash", "savings.investments",
    "other.uncategorized",
]


class CategoryGuess(BaseModel):
    category: str
    confidence: float


def categorize_merchant(merchant_clean: str) -> CategoryGuess:
    """
    Wola lokalna Ollame z wymuszonym schematem JSON (nie tylko format='json').
    Temperature=0, zeby zmaksymalizowac trzymanie sie schematu i fixed listy.
    """
    client = Client(host=settings.ollama_base_url)

    prompt = (
        "Przypisz sprzedawce dokladnie jedna kategorie z tej listy:\n"
        f"{', '.join(CATEGORIES)}\n\n"
        f"Sprzedawca: {merchant_clean}\n"
        "Zwroc kategorie z listy oraz pewnosc 0-1. "
        "Jesli nie pasuje nic sensownego, zwroc other.uncategorized."
    )

    response = client.chat(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}],
        format=CategoryGuess.model_json_schema(),
        options={"temperature": 0},
    )

    guess = CategoryGuess.model_validate_json(response.message.content)
    # bezpiecznik: jesli model mimo schematu wymysli kategorie spoza listy,
    # nie ufamy mu i oznaczamy jako uncategorized zamiast psuc fixed liste
    if guess.category not in CATEGORIES:
        return CategoryGuess(category="other.uncategorized", confidence=0.0)
    return guess
