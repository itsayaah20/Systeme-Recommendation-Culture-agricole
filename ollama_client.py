# ollama_client.py
import requests

def call_ollama_api(prompt, model="mistral", temperature=0.7):
    """
    Appelle l'API Ollama pour générer une réponse.

    Args:
        prompt (str): Le prompt à envoyer au modèle.
        model (str): Le nom du modèle Ollama à utiliser (par défaut 'mistral').
        temperature (float): La température pour la génération (contrôle la créativité).

    Returns:
        str: La réponse générée par le modèle Ollama.
    Raises:
        requests.exceptions.RequestException: Si la requête à l'API Ollama échoue.
        ValueError: Si la réponse de l'API est inattendue.
    """
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,  # We want a single response, not a stream
        "options": {
            "temperature": temperature
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        # The generated text is typically in result['response'] for non-streaming
        if 'response' in result:
            return result['response'].strip()
        elif 'error' in result:
            raise ValueError(f"Ollama API returned an error: {result['error']}")
        else:
            raise ValueError("Unexpected response format from Ollama API.")

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error connecting to Ollama API: {e}")
    except ValueError as e:
        raise ValueError(f"Error processing Ollama API response: {e}")