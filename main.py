from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime, timedelta

app = FastAPI(title="BudgetTrip API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DUFFEL_KEY = os.environ.get("DUFFEL_KEY", "")   


@app.get("/")
async def root():
    return {"status": "ok", "app": "BudgetTrip API"}


@app.get("/search")
async def search_trip(
    origin: str,
    destination: str,
    date: str,
    budget: float,
    nights: int = 3
):
    flight_cost = 0
    flight_detail = "Nema letova"
    flight_link = ""

    try:
        return_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=nights)).strftime("%Y-%m-%d")

        resp = requests.post(
            "https://api.duffel.com/flights/searches",
            headers={
                "Authorization": f"Bearer {DUFFEL_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "adults": 1,
                "cabin_class": "economy",
                "sell_from": "EU",
                "itinerary_type": "round_trip",
                "segments": [
                    {
                        "origin_iata_code": origin,
                        "destination_iata_code": destination,
                        "departure_date": date,
                    },
                    {
                        "origin_iata_code": destination,
                        "destination_iata_code": origin,
                        "departure_date": return_date,
                    },
                ],
            },
            timeout=15,
        )

        if resp.status_code == 200:
            search_id = resp.json()["id"]
            resp2 = requests.get(
                f"https://api.duffel.com/flights/searches/{search_id}/results",
                headers={"Authorization": f"Bearer {DUFFEL_KEY}"},
                params={"sort": "price", "per_page": 1},
                timeout=15,
            )
            if resp2.status_code == 200:
                results = resp2.json()
                if results:
                    best = results[0]
                    flight_cost = int(best["price"]["total"]["value"]) / 100
                    dep = best["segments"][0]["departure_time"][:16].replace("T", " ")
                    arr = best["segments"][1]["arrival_time"][:16].replace("T", " ")
                    flight_detail = f"Round trip | Odlazak: {dep} | Povratak: {arr}"
                    flight_link = "https://www.duffel.com"
        else:
            flight_detail = f"Duffel HTTP {resp.status_code}"
    except Exception as e:
        flight_detail = f"Greška: {str(e)[:50]}"

    bus_cost = 0
    bus_detail = "Provjeri FlixBus"
    bus_link = f"https://www.flixbus.com/en/search?departureCity={origin}&arrivalCity={destination}"

    hotel_cost = 35 * nights
    hotel_detail = f"Hostel, {nights} noci (procjena)"
    hotel_link = f"https://www.booking.com/searchresults.html?ss={destination}&checkin={date}&group_adults=1&no_rooms=1"

    food_per_day = 25
    food_cost = food_per_day * nights
    food_detail = f"{nights} dana x {food_per_day} EUR/dan"
    food_link = f"https://www.numbeo.com/cost-of-living-in-{destination.lower()}"

    total = flight_cost + bus_cost + hotel_cost + food_cost
    remaining = budget - total

    return {
        "budget": budget,
        "nights": nights,
        "flight": {"cost": round(flight_cost, 2), "detail": flight_detail, "link": flight_link},
        "bus": {"cost": bus_cost, "detail": bus_detail, "link": bus_link},
        "hotel": {"cost": hotel_cost, "detail": hotel_detail, "link": hotel_link},
        "food": {"cost": food_cost, "detail": food_detail, "link": food_link},
        "total": round(total, 2),
        "remaining": round(remaining, 2),
        "fits_budget": remaining >= 0,
    }   
