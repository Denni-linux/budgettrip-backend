# BudgetTrip API

Backend za BudgetTrip aplikaciju — traži jeftini prijevoz, smještaj i hranu unutar zadанog budžeta.

## Stack

- Python 3.12
- FastAPI
- Uvicorn
- Requests (za pozive na RapidAPI)

## Endpoints

| Metoda | Putanja | Opis |
|--------|---------|------|
| `GET` | `/` | Health check |
| `POST` | `/search` | Pretraga puta (origin, destination, date, budget) |

## Parametri `/search`

| Parametar | Tip | Opis |
|-----------|-----|------|
| `origin` | string | IATA kod polazišta (npr. `ZAG`) |
| `destination` | string | IATA kod odredišta (npr. `VIE`) |
| `date` | string | Datum u formatu `YYYY-MM-DD` |
| `budget` | float | Ukupni budžet u EUR |

## Pokretanje lokalno

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000   
