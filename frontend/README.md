# Days on Market — Frontend

Interface de prédiction du temps de vente d'un bien immobilier.  
Construite avec **React 18** + **TypeScript** + **Vite** + **Tailwind CSS**.

---

## Lancer le projet

### Avec Docker (recommandé)

```bash
# Depuis la racine du projet
docker compose up --build -d
```

L'interface est disponible sur **`http://localhost:80`**.

> Le frontend communique avec le backend via nginx — aucune configuration supplémentaire.

### En local (sans Docker)

```bash
cd frontend
npm install
npm run dev
```

L'interface est disponible sur **`http://localhost:5173`**.

> En local sans Docker, le backend doit tourner séparément sur le port 8000.  
> Créer un fichier `.env` à la racine de `frontend/` :
> ```
> VITE_API_BASE_URL=http://localhost:8000
> ```

---

## Qualité de code

### Outils

| Outil | Rôle | Config |
|---|---|---|
| **ESLint** | Linter TypeScript/React (règles `@typescript-eslint` + `react-hooks`) | `eslint.config.js` |
| **Prettier** | Formatter automatique (quotes, indentation, virgules...) | `.prettierrc` |

### Lancer les checks (via Docker)

Les checks s'exécutent dans un service Docker dédié `frontend-lint` (image `node:20-alpine`) qui ne démarre **pas** avec `docker compose up` — uniquement via `--profile lint`.

```bash
# Lint — détecte les erreurs TypeScript/React
docker compose --profile lint run --rm frontend-lint npm run lint

# Vérifier le formatage sans modifier les fichiers
docker compose --profile lint run --rm frontend-lint npm run format:check

# Appliquer le formatage automatiquement
docker compose --profile lint run --rm frontend-lint npm run format

# Corriger les erreurs ESLint auto-fixables
docker compose --profile lint run --rm frontend-lint npm run lint:fix
```

> **Premier lancement :** le service installe automatiquement `node_modules` dans un volume Docker nommé (`frontend_node_modules`). Les lancements suivants réutilisent ce cache — l'installation ne se refait que si `node_modules` est vide.

### Scripts disponibles (`package.json`)

| Script | Commande | Description |
|---|---|---|
| `lint` | `eslint src` | Vérifie tout le dossier `src/` |
| `lint:fix` | `eslint src --fix` | Corrige les erreurs auto-fixables |
| `format` | `prettier --write src` | Reformatte tous les fichiers |
| `format:check` | `prettier --check src` | Vérifie sans modifier |

### Git hook automatique

Le hook `.git/hooks/pre-commit` exécute ESLint et Prettier avant chaque `git commit`. Si un check échoue, le commit est bloqué.

---

## Tests

### Outils

| Outil | Rôle | Config |
|---|---|---|
| **Vitest** | Test runner natif Vite — réutilise la config Vite sans configuration supplémentaire | `vite.config.ts` |
| **@testing-library/react** | Monte les composants dans un DOM virtuel et permet de les interroger | — |
| **@testing-library/jest-dom** | Matchers expressifs : `toBeInTheDocument`, `toHaveTextContent`, `toHaveClass`... | `src/test/setup.ts` |
| **jsdom** | Simule un environnement DOM complet sans navigateur réel | — |

### Lancer les tests (via Docker)

Les tests s'exécutent dans le même service Docker `frontend-lint` que le linting.

```bash
# Mode run — lance tous les tests une fois et affiche le résultat (équivalent pytest)
docker compose --profile lint run --rm --remove-orphans frontend-lint npm run test:run

# Mode watch — relance automatiquement les tests à chaque modification de fichier
docker compose --profile lint run --rm --remove-orphans frontend-lint npm run test
```

### Ce qui est testé

#### `PredictionResult` — 8 tests

Composant stateless qui reçoit une `PredictionResponse` et l'affiche en carte.

| Test | Ce qui est vérifié |
|---|---|
| Affichage des jours | Le nombre prédit et le mot "jours" sont présents |
| Formatage du nom | `random_forest` → `Random Forest` (snake_case → Title Case) |
| Intervalle de confiance | `lower_bound` et `upper_bound` arrondis et affichés |
| Couleur verte | `predicted_days ≤ 30` → classe `text-green-600` |
| Couleur orange | `predicted_days ≤ 60` → classe `text-orange-500` |
| Couleur rouge | `predicted_days > 60` → classe `text-red-500` |
| Badge "Recommandé" | Présent quand `highlighted=true` |
| Pas de badge | Absent par défaut (`highlighted` non passé) |

#### `ModelComparison` — 6 tests

Composant qui gère le rendu conditionnel selon `PredictionState.status`.

| Test | Ce qui est vérifié |
|---|---|
| État `idle` | Le composant ne rend rien (`null`) |
| État `loading` | Un spinner (`.animate-spin`) est présent |
| État `error` | Le message d'erreur et son détail sont affichés |
| État `success` | Les 3 cartes de modèles sont affichées |
| Meilleur modèle | Le badge "Recommandé" est unique et sur la bonne carte |
| Titre | "Résultats de prédiction" est affiché en succès |

### Structure des fichiers de test

```
src/
├── test/
│   └── setup.ts                              # Charge @testing-library/jest-dom avant chaque suite
└── components/
    └── results/
        ├── PredictionResult.tsx
        ├── PredictionResult.test.tsx         # 8 tests unitaires
        ├── ModelComparison.tsx
        └── ModelComparison.test.tsx          # 6 tests unitaires
```

> Les tests sont aussi exécutés automatiquement par le hook `.git/hooks/pre-commit` avant chaque `git commit`, après ESLint et Prettier.

---

## Utiliser le formulaire

### Vue d'ensemble

```
┌─────────────────────────┬──────────────────────────────────────┐
│     Formulaire (17      │         Résultats (3 modèles)        │
│       champs)           │                                      │
│                         │   XGBoost   Random F.   Lin. Reg.   │
│  [Infos bien]           │   ┌──────┐  ┌──────┐  ┌──────┐     │
│  [Localisation]         │   │ 47 j │  │ 52 j │  │ 61 j │     │
│  [Aménités]             │   └──────┘  └──────┘  └──────┘     │
│                         │                                      │
│  [Prédire]              │  Intervalle de confiance à 95%       │
└─────────────────────────┴──────────────────────────────────────┘
```

Remplir le formulaire → cliquer **"Prédire le temps de vente"** → les 3 modèles répondent simultanément.

Le modèle avec la prédiction la plus courte est mis en avant avec le badge **Recommandé**.

---

### Les champs du formulaire

#### Informations sur le bien

| Champ | Description | Valeur par défaut |
|---|---|---|
| Surface (m²) | Superficie habitable | 65 |
| Nombre de pièces | Pièces principales | 3 |
| Salles de bain | | 1 |
| Âge du bien | En années (0 = neuf) | 15 |
| Prix de vente | Prix demandé en € | 320 000 |
| Prix marché au m² | Prix moyen de la zone en €/m² | 4 800 |
| Étage | 0 = rez-de-chaussée | 2 |
| Type de bien | Appartement, Maison, Studio, Penthouse, Loft | Appartement |
| Diagnostic énergétique | De A (meilleur) à G (pire) | C |
| État général | Neuf, Bon état, Moyen, Mauvais état | Bon état |

#### Localisation

| Champ | Description | Valeur par défaut |
|---|---|---|
| Ville | | Paris |
| Quartier | | Montmartre |
| Code postal | 5 chiffres | 75018 |

#### Aménités

| Champ | Description | Valeur par défaut |
|---|---|---|
| Balcon | Cochée = oui | ✓ |
| Terrasse | Cochée = oui | ✗ |
| Parking | Cochée = oui | ✓ |
| Meublé | Cochée = oui | ✗ |

> **Note :** `price_ratio` (surévaluation vs marché) est calculé automatiquement par le backend à partir du prix, de la surface et du prix marché. Ce champ ne figure pas dans le formulaire.

---

### Interpréter les résultats

Chaque carte de résultat affiche :

```
┌─────────────────────────┐
│ XGBoost      Recommandé │   ← modèle le plus rapide mis en avant
│                         │
│        47 jours         │   ← prédiction centrale
│                         │
│  Intervalle 95%         │
│     28 – 66 jours       │   ← fourchette de confiance
└─────────────────────────┘
```

**Lecture :** *"Ce bien devrait se vendre en 47 jours. On est à 95% certain qu'il se vendra entre 28 et 66 jours."*

La couleur du chiffre indique la rapidité estimée :
- **Vert** → ≤ 30 jours (vente rapide)
- **Orange** → entre 31 et 60 jours
- **Rouge** → > 60 jours (vente longue)

---

### Tester rapidement des cas extrêmes

**Bien surévalué — devrait rester longtemps sur le marché :**
- Prix de vente : `600 000 €` pour une surface de `50 m²` avec un marché à `4 000 €/m²`
- État : `Mauvais état`, DPE : `G`

**Bien attractif — devrait se vendre vite :**
- Prix de vente : `180 000 €` pour une surface de `60 m²` avec un marché à `4 000 €/m²`
- État : `Neuf`, DPE : `A`, Parking coché

---

## Architecture

```
src/
├── types/index.ts          # Contrats TypeScript (PredictionRequest, PredictionResponse…)
├── api/
│   ├── client.ts           # Instance Axios configurée (baseURL, timeout)
│   └── endpoints.ts        # Fonctions d'appel HTTP (fetchAllPredictions, fetchModels…)
├── hooks/
│   ├── usePrediction.ts    # Gère le cycle idle → loading → success/error
│   └── useModels.ts        # Charge la liste des modèles au montage
├── components/
│   ├── form/               # Formulaire découpé en 3 sections (PropertyInfo, Location, Amenities)
│   └── results/            # Affichage des résultats (PredictionResult, ModelComparison)
└── pages/
    └── HomePage.tsx        # Assemble formulaire + résultats, gère le "lift state up"
```

---

## Variables d'environnement

| Variable | Description | Local Docker | Production Vercel |
|---|---|---|---|
| `VITE_API_BASE_URL` | URL de base du backend | *(vide)* | URL Render (ex: `https://…onrender.com`) |

En local Docker, la variable est vide : nginx proxifie `/api/` vers `backend:8000` automatiquement.
