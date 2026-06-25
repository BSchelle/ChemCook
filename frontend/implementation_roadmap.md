# ChemCook Streamlit Roadmap

## 1. Implémentations passées

- API FastAPI disponible sur `POST /api/v1/calculations/preview`.
- Calcul chimique conservé dans `backend/app/services/calculation_service.py`.
- Modèles Pydantic partagés entre la route et le calcul.
- Tests backend pour le moteur, le service et la route HTTP.

## 2. Implémentation Streamlit

- Formulaire de saisie des espèces, des quantités et des paramètres globaux.
- Appel HTTP vers l'API via `httpx`.
- Affichage du réactif limitant, de `xmax`, des moles, des masses et du tableau d'avancement.
- Affichage du JSON brut pour déboguer les écarts de sérialisation.

## 3. Suite à venir

- Ajouter des presets de réactions pour accélérer les saisies.
- Ajouter la validation UX côté front avant l'envoi au backend.
- Proposer un mode d'édition plus ergonomique pour les espèces.
