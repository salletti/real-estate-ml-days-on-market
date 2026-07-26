# Pipeline de Preprocessing

Les modèles de Machine Learning manipulent des nombres. Les données immobilières contiennent des nombres, des catégories textuelles, des valeurs ordonnées et des booléens. Le backend transforme donc toutes les entrées avant l'entraînement et la prédiction.

Le projet utilise un `ColumnTransformer` scikit-learn dans un `Pipeline`.

## Features Numériques

Exemples :

- `surface`
- `rooms`
- `bathrooms`
- `age`
- `listing_price`
- `market_price_m2`
- `floor`

Elles sont transformées avec `StandardScaler`.

```text
valeur_standardisée = (valeur - moyenne) / écart_type
```

Cela évite qu'une feature avec une grande unité, comme un prix en euros, domine artificiellement une feature plus petite, comme le nombre de pièces.

## Features Ordinales

Une feature ordinale possède un ordre logique.

Exemples :

```text
energy_rating : A, B, C, D, E, F, G
condition     : new, good, fair, poor
```

Elles sont encodées avec `OrdinalEncoder`, en conservant cet ordre.

```text
A -> 0
B -> 1
C -> 2
...
G -> 6
```

## Features Catégorielles

Une feature catégorielle n'a pas d'ordre naturel.

Exemples :

- `property_type`
- `city`
- `neighborhood`
- `zipcode`

Elles sont encodées avec `OneHotEncoder`.

```text
property_type="house"  -> [0, 1, 0, 0]
property_type="studio" -> [0, 0, 1, 0]
```

Utiliser des labels numériques simples, comme `house=2` et `studio=3`, créerait un ordre artificiel. Le one-hot encoding évite ce problème.

## Features Binaires

Les features binaires sont déjà exploitables :

- `balcony`
- `terrace`
- `parking`
- `furnished`

Elles passent directement dans le modèle.

## ColumnTransformer

`ColumnTransformer` applique chaque transformation au bon groupe de colonnes, puis concatène le résultat dans une matrice numérique.

```text
colonnes numériques     -> StandardScaler
colonnes ordinales      -> OrdinalEncoder
colonnes catégorielles  -> OneHotEncoder
colonnes binaires       -> passthrough
```

## Pipeline

Le preprocessor et le modèle sont réunis dans un `Pipeline` scikit-learn.

```python
Pipeline([
    ("preprocessor", ColumnTransformer(...)),
    ("model", XGBRegressor(...)),
])
```

C'est important : les mêmes transformations sont utilisées à l'entraînement et à l'inférence. Le fichier `.joblib` sauvegardé contient le pipeline complet, pas seulement le modèle final.

## Inférence

À la prédiction, l'API reçoit des données brutes depuis le frontend :

```json
{
  "surface": 75,
  "listing_price": 320000,
  "city": "Paris",
  "energy_rating": "C"
}
```

Le pipeline transforme ces données automatiquement avant de produire la prédiction.
