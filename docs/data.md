# Dataset et Features

Le projet utilise un dataset synthétique de 5 000 biens immobiliers.

## Pourquoi des Données Synthétiques ?

Un dataset immobilier propre, libre et directement exploitable est difficile à obtenir. Les données synthétiques rendent le projet reproductible et pédagogique, car les relations entre features et target sont contrôlées.

Cela signifie aussi que le projet n'est pas un système de prédiction prêt pour la production. Le comportement des modèles reflète les règles de génération du dataset.

## Features d'Entrée

| Feature | Type | Description |
|---|---|---|
| `surface` | numérique | Superficie en m2 |
| `rooms` | numérique | Nombre de pièces |
| `bathrooms` | numérique | Nombre de salles de bain |
| `age` | numérique | Ancienneté du bien en années |
| `listing_price` | numérique | Prix demandé en euros |
| `market_price_m2` | numérique | Prix moyen local au m2 |
| `floor` | numérique | Étage, avec 0 pour rez-de-chaussée |
| `energy_rating` | ordinal | DPE de A à G |
| `condition` | ordinal | État : new, good, fair, poor |
| `property_type` | catégoriel | apartment, house, studio, penthouse, loft |
| `city` | catégoriel | Ville |
| `neighborhood` | catégoriel | Quartier |
| `zipcode` | catégoriel | Code postal |
| `balcony` | binaire | Présence d'un balcon |
| `terrace` | binaire | Présence d'une terrasse |
| `parking` | binaire | Présence d'un parking |
| `furnished` | binaire | Bien meublé ou non |

## Target

La target est :

```text
days_on_market
```

Elle représente le nombre de jours entre la mise en vente et la vente du bien.

## Construction de la Target

La target synthétique est générée avec des règles inspirées de l'immobilier :

```text
days = base
     + impact de la surévaluation
     + pénalité liée à l'état
     + pénalité liée au DPE
     + effet du type de bien
     - effet des équipements
     + bruit aléatoire
```

Le bruit aléatoire est volontaire. Deux biens similaires ne se vendent pas forcément exactement au même moment.

## Feature Dérivée Principale

La feature la plus importante est :

```text
price_ratio = listing_price / (surface * market_price_m2)
```

Interprétation :

| Valeur | Signification |
|---|---|
| `1.0` | Bien affiché au prix estimé du marché |
| `1.30` | Bien surévalué d'environ 30% |
| `0.85` | Bien sous-évalué d'environ 15% |

Cette feature est calculée automatiquement par le backend. Elle n'est pas saisie par l'utilisateur.

## Données Réelles

Pour un usage réel, les données synthétiques devraient être remplacées ou complétées avec des données de marché :

- données DVF en France
- historique d'annonces
- temps de publication réel des annonces
- signaux géographiques
- tendances temporelles du marché
