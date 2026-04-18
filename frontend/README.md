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
