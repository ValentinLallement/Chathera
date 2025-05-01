import requests
import json
from datetime import datetime
from app.config import GROK_API_KEY, GROK_URL  # Ces valeurs doivent être définies dans config.py
from typing import List
def build_prompt(messages_recents: List[dict], dernier_message: dict,
                 memoire_court_terme: List, memoire_long_terme: List) -> str:
    # Fonction pour obtenir la date actuelle au format 'YYYY-MM-DD HH:MM:SS'
    def get_current_date():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fonction de formatage de mémoire
    def format_memoires(memoires: List) -> str:
        return "\n".join(
            f"- ({m.created_at.strftime('%Y-%m-%d %H:%M:%S')}) [{m.type}] : {m.contenu}"
            for m in memoires
        ) if memoires else "Aucune"

    # 🔍 Vérification de l'existence de messages récents
    if not messages_recents:
        print("Attention : Aucun message récent trouvé.")

    # 🧱 Formatage des messages récents
    messages_str = "\n".join(
        f"({msg.get('date', get_current_date())}) - {msg.get('auteur', 'Auteur inconnu')} : {msg.get('contenu', 'Contenu inconnu')}"
        for msg in messages_recents
    )

    # 🔍 Vérification et formatage du dernier message
    dernier_str = f"({dernier_message.get('date', get_current_date())}) - {dernier_message.get('auteur', 'Auteur inconnu')} : {dernier_message.get('contenu', 'Contenu inconnu')}"

    # 📦 Construction du prompt à envoyer au LLM
    prompt = f"""Tu es une IA intégrée dans une messagerie. Ta tâche est d'analyser la conversation récente et d'interagir de manière appropriée en fonction du contexte, des messages et de l'état émotionnel de l'utilisateur. Tu dois simuler le meilleur comportement humain que ce soit dans les réponses ou les actions à prendre. Tu dois :

1. **Analyser les messages récents** :
   - Si l'utilisateur semble fatigué, stressé, ou juste vouloir être laissé seul, il peut répondre brièvement ("Ok", "D'accord", "Bonne nuit") sans nécessairement initier une grande conversation.
   - Si l'utilisateur semble ouvert, en demande de soutien, ou cherche à engager davantage la conversation, tu peux répondre de manière plus détaillée (pas plus de 2 phrases ou 3 grand max)

2. **Mettre à jour la mémoire** :
   - **Mémoire court terme** : Enregistre tous les messages récents (et l'état émotionnel immédiat de l'utilisateur.)
   - **Mémoire long terme** : Note les comportements récurrents de l'utilisateur (par exemple, il répond brièvement en fin de journée, il cherche du soutien quand il est stressé, etc…), ses préférences, date importante, ce qu’il dit d’important sur lui, les choses importantes en général pour qu'elles puissent être réutilisées dans une conversation)

3. **Répondre de manière appropriée** :
   - Si une réponse est nécessaire : génère une réponse adaptée à l'humeur et à la situation (empathique, calme, amicale, etc.).
   - Si aucune réponse n'est nécessaire mais que tu dois montrer que l'IA comprend la situation, utilise des réponses simples comme "Ok", "Bonne nuit", "D'accord", en tenant compte de la date et de l'heure.

4. **Estimer la prochaine initiation** :
   - ta réponse doit contenir les prochains messages à envoyer (ça peut être un rappel demandé par l’utilisateur, un anniversaire à souhaiter, etc.)
   - Prends en compte l'heure et la situation pour décider du moment de relancer

5. **Structure de la réponse** :
   - **nouvelle_memoire** : Met à jour la mémoire avec les informations pertinentes.
   - **message** : Le message à envoyer à l'utilisateur (si l'IA doit répondre).
   - **action** : L'action à entreprendre : "répondre", "ne pas répondre", "attendre", "relancer plus tard".
   - **date_action** : La date à laquelle l'action doit être effectuée (si applicable).

---

### Mémoire court terme :
{format_memoires(memoire_court_terme)}

### Mémoire long terme :
{format_memoires(memoire_long_terme)}

---

### Conversation récente :
#### Messages récents :
{messages_str}

#### Dernier message utilisateur :
{dernier_str}

#### Analyse de la conversation :
à analyser (mais à ne pas écrire dans l'output !)

#### Sortie attendue (exemple) :

json
{{
  "nouvelle_memoire": [
    {{
      "type": "",
      "contenu": ""
    }}
  ],
  "message": "",
  "action": "",
  "date_action": "",
  "future_action": "",
  "date_future_action": "",
  "future_message": ""
}}
"""
    return prompt

def get_auto_reply_from_grok(prompt: str) -> dict:
    cleaned_token = GROK_API_KEY.strip()  # Retirer les \n ou espaces invisibles

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cleaned_token}"
    }

    payload = {
        "messages": [
            {
                "role": "system",
                "content": "Tu es une IA intégrée dans une messagerie. Tu dois répondre avec un JSON structuré et utile."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "grok-3-latest",
        "stream": False,
        "temperature": 0.4
    }

    # Envoi de la requête POST à l'API
    response = requests.post(GROK_URL, headers=headers, json=payload)
    response.raise_for_status()

    # La réponse contient une chaîne JSON : il faut la parser
    response_data = response.json()

    # Imprimer la réponse brute pour débogage
    print("Réponse brute de Grok : ", response_data)

    # Vérifier la structure de la réponse
    if "choices" in response_data:
        choices = response_data["choices"]
        
        if len(choices) > 0:
            # Extraire le premier choix et vérifier la structure attendue
            choice = choices[0]
            
            # Vérification de la présence du message
            if "message" in choice and "content" in choice["message"]:
                message_content = choice["message"]["content"]
                
                # Essayer de parser le contenu du message qui devrait être un JSON
                try:
                    parsed_content = json.loads(message_content)
                    
                    # Extraire la réponse, la mémoire, et les actions futures
                    message = parsed_content.get("message", "Message par défaut")
                    receiver_id = parsed_content.get("receiver_id", "ID inconnu")
                    memories = parsed_content.get("nouvelle_memoire", [])
                    future_action = parsed_content.get("future_action", None)
                    date_future_action = parsed_content.get("date_future_action", None)
                    future_message = parsed_content.get("future_message", None)

                    # Retourner un dictionnaire structuré avec les données complètes
                    return {
                        "message": message,
                        "receiver_id": receiver_id,
                        "memories": memories,
                        "future_action": future_action,
                        "date_future_action": date_future_action,
                        "future_message": future_message
                    }
                    
                except json.JSONDecodeError:
                    print("Erreur lors du parsing du contenu JSON.")
                    return {"error": "Impossible de parser le message JSON."}
            else:
                print("La réponse ne contient pas les informations attendues.")
                return {"error": "Réponse mal formée."}
        else:
            print("Aucune réponse trouvée dans 'choices'.")
            return {"error": "Pas de choix dans la réponse."}
    else:
        print("La réponse de Grok ne contient pas de clé 'choices'.")
        return {"error": "Clé 'choices' manquante."}
