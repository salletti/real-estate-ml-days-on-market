# Comparaison des Modèles

Days on Market compare trois modèles de régression :

- Linear Regression
- Random Forest
- XGBoost

Chaque modèle est entraîné sur le même dataset et évalué avec les mêmes métriques.

## Linear Regression

La régression linéaire sert de baseline. Elle apprend une relation linéaire directe entre les features et la target.

```text
days = a * surface + b * price + c * age + ... + constante
```

Forces :

- rapide
- simple
- interprétable
- utile comme point de référence

Limites :

- ne découvre pas naturellement les relations non linéaires
- ne découvre pas les ratios ou interactions complexes si on ne les fournit pas explicitement

C'est pour cela que `price_ratio` a un impact important.

## Random Forest

Random Forest est un ensemble d'arbres de décision. Chaque arbre est entraîné sur un sous-ensemble légèrement différent des données. La prédiction finale est la moyenne des prédictions des arbres.

Forces :

- robuste
- capture des relations non linéaires
- moins sensible au bruit qu'un seul arbre
- permet d'estimer une incertitude via la dispersion entre arbres

Limites :

- plus lourd qu'une régression linéaire
- souvent moins précis que le gradient boosting sur données tabulaires

## XGBoost

XGBoost est un modèle de gradient boosting. Les arbres sont entraînés séquentiellement : chaque nouvel arbre corrige les erreurs des précédents.

```text
arbre 1 -> prédiction initiale
arbre 2 -> correction des erreurs résiduelles
arbre 3 -> correction des erreurs restantes
...
```

Forces :

- très performant sur données tabulaires
- capture les relations non linéaires et les interactions
- souvent excellent sur les datasets structurés

Limites :

- demande plus de tuning
- peut surapprendre si les paramètres sont mal choisis

## Intervalles de Confiance

Le projet utilise une stratégie différente selon le modèle.

| Modèle | Stratégie |
|---|---|
| XGBoost | Modèles de quantile regression pour les bornes basse et haute |
| Random Forest | Dispersion entre les arbres |
| Linear Regression | Écart type global des résidus |

## Quantile Regression avec XGBoost

Pour XGBoost, deux modèles internes supplémentaires sont entraînés :

- `xgboost_q10` : borne basse
- `xgboost_q90` : borne haute

Ils ne sont pas exposés comme modèles sélectionnables, mais ils sont utilisés automatiquement lors d'une prédiction avec XGBoost.

Cette approche produit des intervalles adaptés à chaque bien, au lieu d'appliquer la même marge à toutes les prédictions.

## Impact du Feature Engineering

La feature la plus importante est `price_ratio`.

```text
price_ratio = listing_price / (surface * market_price_m2)
```

Avant cette feature, les modèles devaient deviner la relation entre prix, surface et prix local. Après son ajout, le signal de prix devient explicite.

Leçon principale :

> Un modèle simple avec de bonnes features peut concurrencer un modèle plus complexe avec de mauvaises features.

## Pistes d'Amélioration

- tuning d'hyperparamètres avec `GridSearchCV` ou recherche aléatoire
- validation croisée pour des métriques plus robustes
- comparaison avec LightGBM ou CatBoost
- validation temporelle avec entraînement sur données anciennes et test sur données récentes
- entraînement sur données réelles de transaction ou d'annonces
