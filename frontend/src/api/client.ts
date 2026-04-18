// =============================================================================
// API CLIENT — Configuration centrale d'Axios
//
// Toute communication avec le backend passe par cet objet "apiClient".
// On le configure une fois ici, et on l'importe partout ailleurs.
// =============================================================================

import axios from 'axios';

// -----------------------------------------------------------------------------
// BASE URL — où se trouve le backend ?
//
// On lit la variable d'environnement VITE_API_BASE_URL injectée par Vite.
// Deux cas possibles :
//
//   1. En local avec Docker  → la variable est VIDE ("")
//      nginx écoute sur localhost:80 et proxifie /api/ → backend:8000
//      Donc baseURL = "" signifie : même hôte, même port que le frontend.
//
//   2. En production (Vercel + Render) → la variable vaut l'URL Render
//      Ex: "https://days-on-market-api.onrender.com"
//      Le frontend Vercel appelle directement le backend Render.
//
// La syntaxe `import.meta.env` est propre à Vite (équivalent de process.env
// dans Create React App). Toute variable doit commencer par VITE_ pour être
// exposée au navigateur.
// -----------------------------------------------------------------------------
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

// -----------------------------------------------------------------------------
// INSTANCE AXIOS
//
// axios.create() retourne une instance configurée (≠ axios global).
// Bonne pratique : ne jamais utiliser axios directement dans les composants,
// toujours passer par cette instance pour centraliser la config.
// -----------------------------------------------------------------------------
const apiClient = axios.create({
  baseURL: BASE_URL,

  // Timeout : si le backend ne répond pas en 10s, on abandonne la requête
  // (évite que l'UI reste bloquée indéfiniment)
  timeout: 10_000,

  headers: {
    // On indique au backend qu'on envoie et qu'on attend du JSON
    'Content-Type': 'application/json',
  },
});

export default apiClient;
