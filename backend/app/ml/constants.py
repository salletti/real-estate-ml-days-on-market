"""
constants.py
------------
Source de vérité unique pour toutes les features du projet.

Pourquoi ce fichier existe :
  Un modèle ML est très sensible à l'ordre des colonnes. Si tu entraînes
  avec ["surface", "rooms", "age"] et qu'à l'inférence tu envoies
  ["age", "surface", "rooms"], le modèle lit des valeurs complètement
  décalées — sans lever d'erreur. Le bug est silencieux et destructeur.

  En centralisant ici la définition et l'ordre des features, trainer.py
  et predictor.py importent la MÊME liste. Il ne peut pas y avoir de
  divergence entre entraînement et inférence.
"""


# ----------------------------------------------------------------------
# Features numériques continues
# ----------------------------------------------------------------------
# Ces colonnes contiennent des nombres avec une échelle variable.
# Elles seront normalisées par StandardScaler (voir preprocessor.py).
#
# surface        : superficie en m² (ex: 45.5)
# rooms          : nombre de pièces (ex: 3)
# bathrooms      : nombre de salles de bain (ex: 1)
# age            : ancienneté du bien en années (ex: 12)
# listing_price  : prix demandé par le vendeur en € (ex: 350 000)
# market_price_m2: prix moyen du m² dans la zone en €/m² (ex: 5 200)
# floor          : étage (0 = rez-de-chaussée, ex: 4)
NUMERIC_FEATURES = [
    "surface",
    "rooms",
    "bathrooms",
    "age",
    "listing_price",
    "market_price_m2",
    "floor",
    # Feature dérivée : rapport entre le prix affiché et le prix de marché.
    # price_ratio = listing_price / (surface × market_price_m2)
    # Ex: price_ratio=1.30 → bien affiché 30% au-dessus du marché.
    # Cette feature capture directement la surévaluation — le facteur principal
    # de days_on_market — sans que le modèle ait à le déduire lui-même.
    # La régression linéaire en bénéficie particulièrement : elle ne sait pas
    # multiplier deux colonnes, mais elle sait utiliser une colonne directement.
    "price_ratio",
]


# ----------------------------------------------------------------------
# Catégories ordinales — valeurs ordonnées de la meilleure à la pire
# ----------------------------------------------------------------------
# Ces listes définissent l'ordre que OrdinalEncoder doit respecter.
# L'ordre EST important : A est meilleur que G, new est meilleur que poor.
# Si on inversait, le modèle apprendrait l'inverse de la réalité.
#
# OrdinalEncoder convertit : A → 0, B → 1, C → 2 ... G → 6
#                            new → 0, good → 1, fair → 2, poor → 3
ORDINAL_ENERGY_CATEGORIES = ["A", "B", "C", "D", "E", "F", "G"]
ORDINAL_CONDITION_CATEGORIES = ["new", "good", "fair", "poor"]

# Noms des colonnes ordinales — dans le même ordre que les listes ci-dessus.
# Le ColumnTransformer fait le lien entre chaque colonne et sa liste de catégories.
ORDINAL_FEATURES = ["energy_rating", "condition"]


# ----------------------------------------------------------------------
# Features catégorielles nominales — valeurs SANS ordre logique
# ----------------------------------------------------------------------
# Ces colonnes contiennent des catégories où l'ordre n'a pas de sens.
# "Paris" n'est pas "supérieur" à "Lyon" — ce sont juste des étiquettes.
# Elles seront transformées en colonnes binaires par OneHotEncoder.
#
# property_type : type de bien ("apartment", "house", "studio"...)
# city          : ville (Paris, Lyon, Marseille...)
# neighborhood  : quartier (Marais, Croix-Rousse...)
# zipcode       : code postal — traité comme catégorie, pas comme nombre
#                 (75001 n'est pas "plus grand" que 69001, c'est juste une zone)
CATEGORICAL_FEATURES = ["property_type", "city", "neighborhood", "zipcode"]


# ----------------------------------------------------------------------
# Features binaires — déjà encodées en 0 ou 1
# ----------------------------------------------------------------------
# Ces colonnes représentent la présence ou l'absence d'un équipement.
# Elles n'ont besoin d'aucune transformation : 0 = absent, 1 = présent.
# Le ColumnTransformer les laisse passer telles quelles ("passthrough").
BINARY_FEATURES = ["balcony", "terrace", "parking", "furnished"]


# ----------------------------------------------------------------------
# Ordre complet et fixe des colonnes
# ----------------------------------------------------------------------
# C'est la liste utilisée dans predictor.py pour construire le DataFrame
# à partir des données envoyées par l'API.
#
# Exemple d'usage dans predictor.py :
#   df = pd.DataFrame([features_dict])[FEATURE_COLUMNS]
#
# Le [FEATURE_COLUMNS] à la fin force pandas à réordonner les colonnes
# dans cet ordre exact — peu importe l'ordre dans lequel l'API les reçoit.
FEATURE_COLUMNS = (
    NUMERIC_FEATURES
    + ORDINAL_FEATURES
    + CATEGORICAL_FEATURES
    + BINARY_FEATURES
)


# ----------------------------------------------------------------------
# Nom de la colonne cible (ce qu'on cherche à prédire)
# ----------------------------------------------------------------------
TARGET = "days_on_market"


# ----------------------------------------------------------------------
# Valeurs autorisées pour les champs catégoriels
# ----------------------------------------------------------------------
# Utilisées dans les schemas Pydantic (validation API) et dans le frontend
# pour peupler les menus déroulants.
PROPERTY_TYPES = ["apartment", "house", "studio", "penthouse", "loft"]
ENERGY_RATINGS = ORDINAL_ENERGY_CATEGORIES   # ["A", "B", "C", "D", "E", "F", "G"]
CONDITIONS = ORDINAL_CONDITION_CATEGORIES    # ["new", "good", "fair", "poor"]
