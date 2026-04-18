"""
preprocessor.py
---------------
Construit le ColumnTransformer : l'objet sklearn qui transforme
un DataFrame de features brutes en une matrice numérique exploitable
par les modèles ML.

Pourquoi c'est nécessaire :
  Les modèles ML sont des fonctions mathématiques — ils ne comprennent
  pas les chaînes de caractères ("Paris", "good", "C"). Tout doit être
  converti en nombres. Selon le type de feature, la conversion est
  différente (d'où les 4 transformations ci-dessous).

Pourquoi un seul objet ColumnTransformer :
  Il apprend les paramètres de transformation sur le train set (.fit),
  puis les applique de façon identique sur le test set et en production
  (.transform). C'est ce qui garantit la cohérence entre entraînement
  et inférence.
"""

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    StandardScaler,
    OrdinalEncoder,
    OneHotEncoder,
)

from app.ml.constants import (
    NUMERIC_FEATURES,
    ORDINAL_FEATURES,
    ORDINAL_ENERGY_CATEGORIES,
    ORDINAL_CONDITION_CATEGORIES,
    CATEGORICAL_FEATURES,
    BINARY_FEATURES,
)


def build_preprocessor() -> ColumnTransformer:
    """
    Retourne un ColumnTransformer prêt à être fitté sur le train set.

    Ce n'est PAS encore entraîné ici — on retourne juste la "recette".
    L'entraînement se fait dans trainer.py via pipeline.fit(X_train, y_train).
    """

    # -------------------------------------------------------------------
    # 1. StandardScaler — features numériques continues
    # -------------------------------------------------------------------
    # Problème : surface (20–300), listing_price (50k–2M) et rooms (1–8)
    # n'ont pas la même échelle. Le modèle interprèterait à tort listing_price
    # comme 10 000x plus "important" que rooms.
    #
    # Solution : pour chaque colonne, soustraire la moyenne et diviser
    # par l'écart-type → toutes les valeurs se retrouvent sur la même échelle
    # (centrées autour de 0, écart-type de 1).
    #
    # Exemple : surface=80m² → 0.3  |  surface=300m² → 2.8  |  surface=20m² → -1.4
    #
    # Important : le scaler apprend la moyenne et l'écart-type sur le TRAIN SET
    # uniquement. Appliquer .fit() sur le test set serait du "data leakage"
    # (contamination des données de test dans l'entraînement).
    numeric_transformer = StandardScaler()

    # -------------------------------------------------------------------
    # 2. OrdinalEncoder — features catégorielles avec un ordre logique
    # -------------------------------------------------------------------
    # Problème : energy_rating ("A"→"G") et condition ("new"→"poor") ont
    # un ordre sémantique réel. A est meilleur que G, new est meilleur que poor.
    #
    # Solution : encoder chaque catégorie par un entier en respectant l'ordre.
    #   energy_rating : A=0, B=1, C=2, D=3, E=4, F=5, G=6
    #   condition     : new=0, good=1, fair=2, poor=3
    #
    # Le modèle peut ainsi apprendre que 6 (G) est associé à plus de jours
    # sur le marché que 0 (A). Cette continuité serait perdue avec OneHotEncoder.
    #
    # handle_unknown="use_encoded_value" + unknown_value=-1 :
    #   Si une valeur inconnue arrive à l'inférence (ex: "H"), le modèle
    #   reçoit -1 au lieu de crasher. Cas rare mais défensif.
    ordinal_transformer = OrdinalEncoder(
        categories=[
            ORDINAL_ENERGY_CATEGORIES,    # ["A", "B", "C", "D", "E", "F", "G"]
            ORDINAL_CONDITION_CATEGORIES, # ["new", "good", "fair", "poor"]
        ],
        handle_unknown="use_encoded_value",
        unknown_value=-1,
    )

    # -------------------------------------------------------------------
    # 3. OneHotEncoder — features catégorielles SANS ordre logique
    # -------------------------------------------------------------------
    # Problème : property_type ("apartment", "house", "studio"...) n'a pas
    # d'ordre. Si on faisait apartment=1, house=2, studio=3, le modèle
    # croirait que "house" est deux fois "apartment" — absurde.
    #
    # Solution : créer une colonne binaire par catégorie.
    #   property_type="house"  →  [0, 1, 0, 0]  (apartment, house, studio, loft)
    #   property_type="studio" →  [0, 0, 1, 0]
    #
    # drop="first" : supprime la première catégorie (ex: "apartment").
    #   Si toutes les autres colonnes sont à 0, on sait que c'est un apartment.
    #   La colonne est redondante et crée de la multicolinéarité (problème
    #   surtout pour la régression linéaire).
    #
    # sparse_output=False : retourne un tableau dense (numpy array)
    #   plutôt qu'une matrice sparse. Plus simple à manipuler pour nous.
    #
    # handle_unknown="ignore" : si une ville inconnue arrive à l'inférence,
    #   toutes ses colonnes sont mises à 0. Le modèle ne plante pas.
    categorical_transformer = OneHotEncoder(
        drop="first",
        sparse_output=False,
        handle_unknown="ignore",
    )

    # -------------------------------------------------------------------
    # 4. passthrough — features binaires (déjà 0 ou 1)
    # -------------------------------------------------------------------
    # balcony, terrace, parking, furnished sont déjà des entiers 0/1.
    # Aucune transformation nécessaire — on les laisse passer tels quels.

    # -------------------------------------------------------------------
    # Assemblage final : ColumnTransformer
    # -------------------------------------------------------------------
    # Chaque tuple = (nom, transformateur, liste_de_colonnes)
    # Le ColumnTransformer applique chaque transformateur sur son groupe
    # de colonnes EN PARALLÈLE, puis concatène les résultats horizontalement.
    #
    # remainder="drop" : toute colonne non listée est ignorée.
    #   Évite que des colonnes inattendues contaminent le modèle.
    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer,     NUMERIC_FEATURES),
            ("ord", ordinal_transformer,     ORDINAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
            ("bin", "passthrough",           BINARY_FEATURES),
        ],
        remainder="drop",
    )
