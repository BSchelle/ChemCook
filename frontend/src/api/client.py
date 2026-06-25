import httpx
from typing import Any, Dict

class ChemCookAPIClient:
    """
    Client API pour communiquer avec le backend FastAPI de ChemCook.
    Encapsule les requêtes HTTP, gère les timeouts et traduit les erreurs techniques.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def preview_calculation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envoie les données de réaction au backend pour calculer la stœchiométrie, 
        le réactif limitant et le tableau d'avancement.
        
        Lève:
            ValueError: Si le backend renvoie une erreur de validation métier (HTTP 400).
            ConnectionError: Si le serveur est injoignable.
            RuntimeError: Pour toute autre erreur HTTP inattendue.
        """
        try:
            response = httpx.post(self.base_url, json=payload, timeout=30.0)
            
            # Gestion spécifique des erreurs de validation métier (HTTP 400)
            if response.status_code == 400:
                try:
                    error_detail = response.json().get("detail", "Erreur de validation des données.")
                except Exception:
                    error_detail = response.text
                raise ValueError(error_detail)
            
            # Lève une exception pour les autres codes 4xx ou 5xx
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Erreur serveur API ({exc.response.status_code}). "
                f"Détail : {exc.response.text}"
            )
        except httpx.RequestError as exc:
            raise ConnectionError(
                "Impossible de se connecter au serveur API de ChemCook. "
                "Veuillez vérifier que le service backend est bien démarré sur le port configuré."
            )
