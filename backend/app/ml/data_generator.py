import numpy as np
import pandas as pd

from app.ml.constants import TARGET


def generate_dataset(n_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # --- Features de base ---
    surface = rng.uniform(20, 300, n_samples)
    rooms = np.clip(rng.integers(1, 8, n_samples), 1, 7).astype(int)
    bathrooms = np.clip(rng.integers(1, rooms + 1), 1, rooms).astype(int)
    age = rng.integers(0, 80, n_samples).astype(int)
    floor = rng.integers(0, 20, n_samples).astype(int)

    market_price_m2 = rng.uniform(2000, 12000, n_samples)
    # Le prix demandé oscille entre -20% et +40% autour du prix de marché
    price_premium = rng.uniform(-0.20, 0.40, n_samples)
    listing_price = np.round(surface * market_price_m2 * (1 + price_premium), -2)

    # Feature dérivée : ratio prix affiché / prix de marché théorique
    # price_ratio=1.0  → bien au prix du marché
    # price_ratio=1.30 → bien surévalué de 30%
    # price_ratio=0.85 → bien sous-évalué de 15% (vente rapide probable)
    # On la calcule ici pour l'entraînement. Elle est aussi calculée dans
    # predictor.py à l'inférence, à partir des features envoyées par l'API.
    price_ratio = listing_price / (surface * market_price_m2)

    # --- Features catégorielles ---
    # Zipcodes réalistes et finis par ville.
    # IMPORTANT : on utilise un set limité de zipcodes (3-4 par ville) plutôt
    # que des valeurs aléatoires. Avec des zipcodes aléatoires, le train set
    # et le test set auraient des zipcodes complètement différents → le
    # OneHotEncoder créerait des milliers de colonnes inutiles, ce qui
    # détruirait les performances (surtout la régression linéaire).
    cities = ["Paris", "Lyon", "Marseille", "Bordeaux", "Lille", "Nantes"]
    neighborhoods = {
        "Paris": ["Marais", "Montmartre", "Bastille", "Nation", "Oberkampf"],
        "Lyon": ["Presquile", "Croix-Rousse", "Part-Dieu", "Vieux-Lyon"],
        "Marseille": ["Vieux-Port", "Castellane", "Prado", "Endoume"],
        "Bordeaux": ["Saint-Pierre", "Chartrons", "Bastide", "Meriadeck"],
        "Lille": ["Vieux-Lille", "Wazemmes", "Fives", "Moulins"],
        "Nantes": ["Bouffay", "Hauts-Paves", "Chantenay", "Doulon"],
    }
    zipcodes = {
        "Paris": ["75001", "75003", "75011", "75018", "75020"],
        "Lyon": ["69001", "69002", "69004", "69006"],
        "Marseille": ["13001", "13002", "13006", "13008"],
        "Bordeaux": ["33000", "33100", "33200", "33300"],
        "Lille": ["59000", "59100", "59160", "59260"],
        "Nantes": ["44000", "44100", "44200", "44300"],
    }
    city_arr = rng.choice(cities, n_samples)
    neighborhood_arr = np.array([rng.choice(neighborhoods[c]) for c in city_arr])
    zipcode_arr = np.array([rng.choice(zipcodes[c]) for c in city_arr])

    property_types = ["apartment", "house", "studio", "penthouse", "loft"]
    # Les studios et appartements sont plus courants
    property_weights = [0.40, 0.25, 0.20, 0.08, 0.07]
    property_type_arr = rng.choice(property_types, n_samples, p=property_weights)

    energy_ratings = ["A", "B", "C", "D", "E", "F", "G"]
    # Les biens récents ont tendance à avoir de meilleures notes
    energy_arr = np.where(
        age < 10,
        rng.choice(["A", "B", "C"], n_samples),
        rng.choice(
            energy_ratings, n_samples, p=[0.05, 0.10, 0.20, 0.25, 0.20, 0.12, 0.08]
        ),
    )

    condition_arr = np.where(
        age < 5,
        "new",
        rng.choice(["good", "fair", "poor"], n_samples, p=[0.50, 0.35, 0.15]),
    )

    balcony = rng.choice([0, 1], n_samples, p=[0.45, 0.55]).astype(int)
    terrace = rng.choice([0, 1], n_samples, p=[0.65, 0.35]).astype(int)
    parking = rng.choice([0, 1], n_samples, p=[0.40, 0.60]).astype(int)
    furnished = rng.choice([0, 1], n_samples, p=[0.70, 0.30]).astype(int)

    # --- Construction de la target : days_on_market ---
    # Base : 30 jours
    days = np.full(n_samples, 30.0)

    # 1. Surévaluation = pénalité principale
    #    Un bien affiché 20% au-dessus du marché prend ~40 jours de plus
    days += price_premium * 200

    # 2. État du bien
    condition_penalty = {"new": 0, "good": 5, "fair": 18, "poor": 35}
    days += np.vectorize(condition_penalty.get)(condition_arr)

    # 3. Note énergétique
    energy_penalty = {"A": -5, "B": -3, "C": 0, "D": 5, "E": 12, "F": 20, "G": 30}
    days += np.vectorize(energy_penalty.get)(energy_arr)

    # 4. Type de bien
    type_effect = {
        "apartment": 0,
        "house": -5,
        "studio": 10,
        "penthouse": -10,
        "loft": -3,
    }
    days += np.vectorize(type_effect.get)(property_type_arr)

    # 5. Aménités (léger effet)
    days -= balcony * 3
    days -= terrace * 4
    days -= parking * 5
    days += furnished * 8  # les meublés se vendent moins vite (investisseurs méfiants)

    # 6. Bruit gaussien (la réalité n'est jamais parfaite)
    days += rng.normal(0, 6, n_samples)

    # On borne les valeurs : minimum 1 jour, maximum 365 jours
    days = np.clip(np.round(days).astype(int), 1, 365)

    return pd.DataFrame(
        {
            "surface": np.round(surface, 1),
            "rooms": rooms,
            "bathrooms": bathrooms,
            "age": age,
            "listing_price": listing_price,
            "market_price_m2": np.round(market_price_m2, 2),
            "price_ratio": np.round(price_ratio, 4),
            "zipcode": zipcode_arr,
            "city": city_arr,
            "neighborhood": neighborhood_arr,
            "property_type": property_type_arr,
            "floor": floor,
            "energy_rating": energy_arr,
            "condition": condition_arr,
            "balcony": balcony,
            "terrace": terrace,
            "parking": parking,
            "furnished": furnished,
            TARGET: days,
        }
    )
