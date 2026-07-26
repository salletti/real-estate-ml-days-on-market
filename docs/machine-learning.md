# Vue d'ensemble Machine Learning

Days on Market répond à une question simple :

> Si ce bien est mis en vente aujourd'hui, combien de jours pourrait-il rester sur le marché ?

Le backend reçoit les caractéristiques d'un bien immobilier : surface, prix, ville, état, DPE, équipements. Il retourne une estimation en jours avec une fourchette de confiance.

## Principe

Un modèle de Machine Learning est une fonction mathématique entraînée sur des exemples.

```text
entrée -> surface=75, prix=320000, ville=Paris, état=good
modèle -> fonction apprise
sortie -> 47 jours
```

Le modèle ne comprend pas l'immobilier comme un humain. Il apprend des relations statistiques dans les données. Par exemple, il peut apprendre qu'un bien surévalué reste généralement plus longtemps sur le marché.

## Features et Target

En Machine Learning, on utilise souvent la convention suivante :

- `X` : les features, c'est-à-dire les variables d'entrée
- `y` : la target, c'est-à-dire la valeur à prédire

Dans ce projet :

```text
X -> surface, rooms, city, energy_rating, parking, listing_price...
y -> days_on_market
```

Le modèle apprend une fonction du type :

```text
y = f(X)
```

## Train et Test

Le dataset est séparé en deux parties avant l'entraînement :

```text
dataset
  -> train set : utilisé pour entraîner le modèle
  -> test set  : utilisé pour évaluer le modèle sur des exemples jamais vus
```

Le modèle voit `X_train` et `y_train` pendant l'entraînement. Ensuite, il prédit uniquement à partir de `X_test`. Les prédictions sont comparées à `y_test` pour calculer les métriques.

Cette séparation évite d'évaluer un modèle sur les mêmes données que celles utilisées pour l'entraîner.

## Métriques

| Métrique | Signification |
|---|---|
| MAE | Erreur absolue moyenne, exprimée en jours |
| RMSE | Erreur qui pénalise davantage les grosses erreurs |
| R2 | Part de variance expliquée par le modèle |

Exemple :

```text
MAE = 15
```

Le modèle se trompe alors d'environ 15 jours en moyenne.

## Fourchette de Confiance

Retourner uniquement `47 jours` serait trop catégorique. L'API retourne aussi une fourchette :

```json
{
  "predicted_days": 47,
  "lower_bound": 28,
  "upper_bound": 66,
  "model_used": "xgboost"
}
```

La fourchette exprime l'incertitude. Un bien typique devrait avoir une fourchette plus serrée qu'un bien atypique ou fortement surévalué.

## Leçon Principale

Le projet montre que le feature engineering peut compter autant que le choix du modèle. La feature `price_ratio` rend explicite le signal de prix et améliore les performances des modèles.
