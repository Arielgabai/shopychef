from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from typing import Dict, List, Any
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Vérifier si la clé API est présente
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("La clé API OpenAI n'est pas définie. Veuillez créer un fichier .env avec OPENAI_API_KEY=votre_clé_api")

app = Flask(__name__)
CORS(app)

# Initialiser le client OpenAI avec la clé API
client = OpenAI(api_key=api_key)

# JavaScript code
JAVASCRIPT_CODE = """
document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('sendButton');
    const userInput = document.getElementById('userInput');
    const response = document.getElementById('response');
    const error = document.getElementById('error');
    const question = document.getElementById('question');
    
    async function sendMessage() {
        const message = userInput.value;

        if (!message) return;

        // Afficher la question
        question.textContent = 'Votre demande : ' + message;
        
        response.textContent = 'Chargement...';
        response.className = 'loading';
        error.textContent = '';
        userInput.value = '';

        try {
            console.log('Envoi de la requête...');
            console.log('Message:', message);
            
            const requestBody = JSON.stringify({ message: message });
            console.log('Corps de la requête:', requestBody);
            
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: requestBody
            });
            
            console.log('Réponse reçue:', res.status);
            
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            
            const data = await res.json();
            console.log('Données reçues:', data);
            
            if (data.error) {
                error.textContent = 'Erreur: ' + data.error;
                response.textContent = '';
                response.className = '';
                return;
            }
            
            if (data.type === 'recipes' && data.data && data.data.recipes && Array.isArray(data.data.recipes)) {
                let formattedResponse = '';
                data.data.recipes.forEach((recipe, index) => {
                    if (!recipe) return;
                    
                    formattedResponse += `Recette ${index + 1}: ${recipe.title || 'Sans titre'}\\n`;
                    formattedResponse += `Pour ${recipe.servings || '?'} personnes\\n`;
                    formattedResponse += `Temps de préparation: ${recipe.prep_time || '?'}\\n`;
                    formattedResponse += `Temps de cuisson: ${recipe.cook_time || '?'}\\n`;
                    formattedResponse += `Difficulté: ${recipe.difficulty || '?'}\\n\\n`;
                    
                    if (recipe.ingredients && Array.isArray(recipe.ingredients)) {
                        formattedResponse += 'Ingrédients:\\n';
                        recipe.ingredients.forEach(ing => {
                            if (ing) {
                                formattedResponse += `- ${ing.quantity || '?'} ${ing.unit || ''} de ${ing.name || '?'}\\n`;
                            }
                        });
                    }
                    
                    if (recipe.steps && Array.isArray(recipe.steps)) {
                        formattedResponse += '\\nÉtapes:\\n';
                        recipe.steps.forEach(step => {
                            if (step) {
                                formattedResponse += `${step.step_number || '?'}. ${step.description || '?'}\\n`;
                            }
                        });
                    }
                    
                    if (recipe.tips && Array.isArray(recipe.tips)) {
                        formattedResponse += '\\nConseils:\\n';
                        recipe.tips.forEach(tip => {
                            if (tip) {
                                formattedResponse += `- ${tip}\\n`;
                            }
                        });
                    }
                    
                    formattedResponse += '\\n' + '-'.repeat(50) + '\\n\\n';
                });
                response.textContent = formattedResponse;
                response.className = '';
            } else {
                response.textContent = 'Format de réponse inattendu. Voici la réponse brute:\\n' + JSON.stringify(data, null, 2);
                response.className = '';
            }
        } catch (error) {
            console.error('Erreur complète:', error);
            document.getElementById('error').textContent = 'Erreur: ' + error.message;
            response.textContent = '';
            response.className = '';
        }
    }

    // Ajouter les écouteurs d'événements
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
"""

# Page d'accueil HTML
HOME_PAGE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Chatbot de Recettes</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .chat-container {{
            border: 1px solid #ccc;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .input-container {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        input[type="text"] {{
            flex: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }}
        button {{
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.2s;
        }}
        button:hover {{
            background-color: #0056b3;
        }}
        #response {{
            margin-top: 20px;
            white-space: pre-wrap;
            line-height: 1.5;
        }}
        .error {{
            color: #dc3545;
            margin-top: 10px;
            padding: 10px;
            border-radius: 5px;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
        }}
        .question {{
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-style: italic;
            color: #495057;
        }}
        .loading {{
            color: #6c757d;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <h1>Chatbot de Recettes</h1>
    <div class="chat-container">
        <div class="question" id="question"></div>
        <div class="input-container">
            <input type="text" id="userInput" placeholder="Ex: Nous sommes 4 et nous voulons manger un plat italien...">
            <button id="sendButton">Envoyer</button>
        </div>
        <div id="response"></div>
        <div id="error" class="error"></div>
    </div>

    <script>
    {JAVASCRIPT_CODE}
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_PAGE)

class RecipeAgent:
    def __init__(self):
        self.tools = {
            "generate_recipes": self.generate_recipes,
            "analyze_ingredients": self.analyze_ingredients,
            "suggest_substitutions": self.suggest_substitutions,
            "calculate_nutrition": self.calculate_nutrition
        }
        
        self.system_prompt = """Tu es un agent IA expert en cuisine qui aide les utilisateurs à créer des recettes personnalisées.
        Tu as accès à plusieurs outils pour répondre aux demandes des utilisateurs :
        1. generate_recipes : Génère des recettes personnalisées
        2. analyze_ingredients : Analyse les ingrédients disponibles
        3. suggest_substitutions : Suggère des substitutions d'ingrédients
        4. calculate_nutrition : Calcule les informations nutritionnelles

        Utilise ces outils de manière appropriée pour répondre aux demandes des utilisateurs."""

    def generate_recipes(self, prompt: str) -> Dict[str, Any]:
        """Génère des recettes personnalisées basées sur le prompt de l'utilisateur"""
        try:
            logger.debug(f"Génération de recettes pour le prompt: {prompt}")
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": """Tu es un chef cuisinier expert qui crée des recettes personnalisées.
                    IMPORTANT: 
                    1. Réponds en JSON valide
                    2. Évite les caractères spéciaux et apostrophes
                    3. Utilise des points au lieu des retours à la ligne
                    4. Utilise uniquement des guillemets doubles
                    5. Inclus tous les champs requis
                    6. Ne duplique pas de contenu
                    7. Sois concis dans les descriptions
                    8. Génère EXACTEMENT 3 recettes différentes
                    9. Chaque recette doit être unique et adaptée à la demande
                    
                    Format JSON requis:
                    {
                        "recipes": [
                            {
                                "title": "Titre",
                                "servings": "Nombre",
                                "prep_time": "Minutes",
                                "cook_time": "Minutes",
                                "difficulty": "Facile/Moyen/Difficile",
                                "ingredients": [
                                    {
                                        "name": "Ingrédient",
                                        "quantity": "Quantité",
                                        "unit": "Unité"
                                    }
                                ],
                                "steps": [
                                    {
                                        "step_number": 1,
                                        "description": "Étape"
                                    }
                                ],
                                "tips": ["Conseil"]
                            }
                        ]
                    }"""},
                    {"role": "user", "content": f"Génère 3 recettes différentes pour: {prompt}"}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Log de la réponse brute
            raw_response = response.choices[0].message.content
            logger.debug(f"Réponse brute de l'API: {raw_response}")
            
            # Nettoyage de la réponse
            cleaned_response = raw_response.strip()
            
            # Suppression des marqueurs de code si présents
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Log après nettoyage initial
            logger.debug(f"Réponse après nettoyage initial: {cleaned_response}")
            
            # Vérification de la validité du JSON avant nettoyage
            if not cleaned_response.startswith('{') or not cleaned_response.endswith('}'):
                logger.error("La réponse n'est pas un objet JSON valide")
                logger.error(f"Contenu reçu: {cleaned_response}")
                return {"error": "Format de réponse invalide"}
            
            # Nettoyage des caractères spéciaux
            cleaned_response = cleaned_response.replace('\n', ' ').replace('\r', ' ')
            cleaned_response = cleaned_response.replace('"', '"').replace('"', '"')
            cleaned_response = cleaned_response.replace(''', "'").replace(''', "'")
            cleaned_response = cleaned_response.replace(''', "'").replace(''', "'")
            
            # Log après nettoyage des caractères spéciaux
            logger.debug(f"Réponse après nettoyage des caractères spéciaux: {cleaned_response}")
            
            try:
                # Tentative de parsing avec gestion des erreurs détaillée
                try:
                    result = json.loads(cleaned_response)
                except json.JSONDecodeError as e:
                    logger.error(f"Erreur de parsing JSON à la position {e.pos}: {e.msg}")
                    logger.error(f"Contexte autour de l'erreur: {cleaned_response[max(0, e.pos-50):min(len(cleaned_response), e.pos+50)]}")
                    return {"error": f"Erreur de parsing JSON: {str(e)}"}
                
                logger.debug(f"Réponse parsée avec succès: {result}")
                
                # Vérification de la structure
                if not isinstance(result, dict):
                    logger.error("La réponse n'est pas un dictionnaire")
                    return {"error": "Structure de réponse invalide"}
                
                if "recipes" not in result:
                    logger.error("La clé 'recipes' est manquante")
                    return {"error": "Structure de réponse invalide"}
                
                if not isinstance(result["recipes"], list):
                    logger.error("La liste des recettes est invalide")
                    return {"error": "Structure de réponse invalide"}
                
                if not result["recipes"]:
                    logger.error("La liste des recettes est vide")
                    return {"error": "Aucune recette générée"}
                
                # Vérification du nombre de recettes
                if len(result["recipes"]) != 3:
                    logger.error(f"Nombre de recettes incorrect: {len(result['recipes'])} au lieu de 3")
                    return {"error": "Le nombre de recettes doit être exactement 3"}
                
                # Nettoyage et validation des données
                cleaned_recipes = []
                for recipe in result["recipes"]:
                    if not isinstance(recipe, dict):
                        logger.error(f"Recette invalide: {recipe}")
                        continue
                    
                    # Vérification des champs requis
                    required_fields = ["title", "servings", "prep_time", "cook_time", "difficulty", "ingredients", "steps", "tips"]
                    for field in required_fields:
                        if field not in recipe:
                            logger.error(f"Champ manquant dans la recette: {field}")
                            recipe[field] = "" if field != "ingredients" and field != "steps" and field != "tips" else []
                    
                    # Nettoyage des champs texte
                    for field in ["title", "servings", "prep_time", "cook_time", "difficulty"]:
                        if field in recipe and recipe[field]:
                            recipe[field] = str(recipe[field]).strip()
                            recipe[field] = recipe[field].replace('\n', ' ').replace('\r', ' ')
                            recipe[field] = recipe[field].replace('"', '"').replace('"', '"')
                            recipe[field] = recipe[field].replace(''', "'").replace(''', "'")
                            recipe[field] = recipe[field].replace(''', "'").replace(''', "'")
                    
                    # Nettoyage des ingrédients
                    if "ingredients" in recipe and isinstance(recipe["ingredients"], list):
                        cleaned_ingredients = []
                        for ing in recipe["ingredients"]:
                            if isinstance(ing, dict):
                                cleaned_ing = {}
                                for field in ["name", "quantity", "unit"]:
                                    if field in ing and ing[field]:
                                        cleaned_ing[field] = str(ing[field]).strip()
                                        cleaned_ing[field] = cleaned_ing[field].replace('\n', ' ').replace('\r', ' ')
                                        cleaned_ing[field] = cleaned_ing[field].replace('"', '"').replace('"', '"')
                                        cleaned_ing[field] = cleaned_ing[field].replace(''', "'").replace(''', "'")
                                        cleaned_ing[field] = cleaned_ing[field].replace(''', "'").replace(''', "'")
                                if cleaned_ing:
                                    cleaned_ingredients.append(cleaned_ing)
                        recipe["ingredients"] = cleaned_ingredients
                    
                    # Nettoyage des étapes
                    if "steps" in recipe and isinstance(recipe["steps"], list):
                        cleaned_steps = []
                        for step in recipe["steps"]:
                            if isinstance(step, dict) and "description" in step and step["description"]:
                                cleaned_step = {
                                    "step_number": step.get("step_number", len(cleaned_steps) + 1),
                                    "description": str(step["description"]).strip()
                                    .replace('\n', ' ')
                                    .replace('\r', ' ')
                                    .replace('"', '"')
                                    .replace('"', '"')
                                    .replace(''', "'")
                                    .replace(''', "'")
                                    .replace(''', "'")
                                    .replace(''', "'")
                                }
                                cleaned_steps.append(cleaned_step)
                        recipe["steps"] = cleaned_steps
                    
                    # Nettoyage des conseils
                    if "tips" in recipe and isinstance(recipe["tips"], list):
                        recipe["tips"] = [
                            str(tip).strip()
                            .replace('\n', ' ')
                            .replace('\r', ' ')
                            .replace('"', '"')
                            .replace('"', '"')
                            .replace(''', "'")
                            .replace(''', "'")
                            .replace(''', "'")
                            .replace(''', "'")
                            for tip in recipe["tips"] if tip
                        ]
                    
                    cleaned_recipes.append(recipe)
                
                # Vérification finale du nombre de recettes
                if len(cleaned_recipes) != 3:
                    logger.error(f"Nombre de recettes incorrect après nettoyage: {len(cleaned_recipes)} au lieu de 3")
                    return {"error": "Le nombre de recettes doit être exactement 3"}
                
                result["recipes"] = cleaned_recipes
                return result
            except Exception as e:
                logger.error(f"Erreur lors du traitement de la réponse: {str(e)}")
                return {"error": str(e)}
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recettes: {str(e)}")
            return {"error": str(e)}

    def analyze_ingredients(self, ingredients: List[str]) -> Dict[str, Any]:
        """Analyse les ingrédients disponibles et suggère des recettes possibles"""
        try:
            logger.debug(f"Analyse des ingrédients: {ingredients}")
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": "Analyse les ingrédients fournis et suggère des recettes possibles."},
                    {"role": "user", "content": f"Analyse ces ingrédients : {', '.join(ingredients)}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return {"analysis": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des ingrédients: {str(e)}")
            return {"error": str(e)}

    def suggest_substitutions(self, ingredient: str) -> Dict[str, Any]:
        """Suggère des substitutions pour un ingrédient donné"""
        try:
            logger.debug(f"Suggestion de substitutions pour: {ingredient}")
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": "Suggère des substitutions possibles pour l'ingrédient fourni."},
                    {"role": "user", "content": f"Quelles sont les meilleures substitutions pour {ingredient} ?"}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return {"substitutions": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Erreur lors de la suggestion de substitutions: {str(e)}")
            return {"error": str(e)}

    def calculate_nutrition(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les informations nutritionnelles pour une recette"""
        try:
            logger.debug(f"Calcul nutritionnel pour la recette: {recipe}")
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": "Calcule les informations nutritionnelles pour la recette fournie."},
                    {"role": "user", "content": f"Calcule les informations nutritionnelles pour cette recette : {json.dumps(recipe)}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return {"nutrition": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Erreur lors du calcul nutritionnel: {str(e)}")
            return {"error": str(e)}

    def process_request(self, user_input: str) -> Dict[str, Any]:
        """Traite la demande de l'utilisateur en utilisant les outils appropriés"""
        try:
            logger.debug(f"Traitement de la demande: {user_input}")
            
            # Si la demande contient des ingrédients ou une demande de recette, utiliser generate_recipes
            if any(keyword in user_input.lower() for keyword in ["recette", "cuisiner", "préparer", "faire", "ingrédients"]):
                recipes = self.generate_recipes(user_input)
                return {
                    "type": "recipes",
                    "data": recipes
                }
            elif "substitution" in user_input.lower():
                # Extraction de l'ingrédient à substituer
                ingredient = user_input.split("substitution")[-1].strip()
                return {
                    "type": "substitutions",
                    "data": self.suggest_substitutions(ingredient)
                }
            else:
                return {
                    "type": "analysis",
                    "data": self.analyze_ingredients([user_input])
                }
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la demande: {str(e)}")
            return {"error": str(e)}

# Créer une instance de l'agent
recipe_agent = RecipeAgent()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        logger.debug(f"Données reçues: {data}")
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({"error": "Le message est requis"}), 400
        
        response = recipe_agent.process_request(user_input)
        print(response)
        logger.debug(f"Réponse générée: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Erreur dans la route /api/chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 