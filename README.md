# Agent IA de Recettes

Ce projet est un agent IA spécialisé en cuisine qui utilise plusieurs outils pour répondre aux demandes des utilisateurs concernant les recettes et la cuisine.

## Prérequis

- Python 3.8 ou supérieur
- Une clé API OpenAI

## Installation

1. Clonez ce dépôt
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configuration de la clé API OpenAI :
   - Créez un fichier `.env` à la racine du projet
   - Ajoutez votre clé API OpenAI dans le fichier :
   ```
   OPENAI_API_KEY=votre_clé_api_openai_ici
   ```
   - Remplacez `votre_clé_api_openai_ici` par votre véritable clé API OpenAI
   - Ne partagez jamais votre clé API et ne la committez pas dans le dépôt Git
   - Ajoutez `.env` à votre fichier `.gitignore` pour éviter de le committer accidentellement

   Pour créer un fichier `.gitignore`, ajoutez ces lignes :
   ```
   .env
   __pycache__/
   *.pyc
   ```

4. Vérifiez que la clé API est bien chargée :
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Clé API présente' if os.getenv('OPENAI_API_KEY') else 'Clé API manquante')"
```

## Sécurité

- Ne partagez jamais votre clé API OpenAI
- Ne committez pas le fichier `.env` dans votre dépôt Git
- Utilisez des variables d'environnement différentes pour le développement et la production
- En production, utilisez un gestionnaire de secrets sécurisé

## Fonctionnalités

L'agent dispose de plusieurs outils pour répondre aux demandes des utilisateurs :

1. **Génération de recettes** (`generate_recipes`)
   - Crée des recettes personnalisées basées sur les critères de l'utilisateur
   - Génère 3 recettes différentes pour chaque demande
   - Inclut les ingrédients, étapes, temps de préparation et conseils

2. **Analyse d'ingrédients** (`analyze_ingredients`)
   - Analyse les ingrédients disponibles
   - Suggère des recettes possibles avec ces ingrédients

3. **Suggestions de substitutions** (`suggest_substitutions`)
   - Propose des alternatives pour un ingrédient donné
   - Inclut des options végétariennes, sans gluten, etc.

4. **Calcul nutritionnel** (`calculate_nutrition`)
   - Calcule les informations nutritionnelles pour une recette
   - Fournit des détails sur les calories, protéines, etc.

## Utilisation

1. Démarrez le serveur :
```bash
python app.py
```

2. Le serveur sera accessible à l'adresse `http://localhost:5000`

3. Pour interagir avec l'agent, envoyez une requête POST à `/api/chat` avec un JSON contenant votre message :
```json
{
    "message": "Nous sommes 4 et nous voulons manger un plat italien avec de la sauce tomate, du chocolat et de la mangue"
}
```

## Format de réponse

La réponse sera au format JSON avec le type de réponse et les données correspondantes :

```json
{
    "type": "recipes",
    "data": {
        "recipes": [
            {
                "title": "Titre de la recette",
                "servings": "Nombre de personnes",
                "prep_time": "Temps de préparation en minutes",
                "cook_time": "Temps de cuisson en minutes",
                "difficulty": "Facile/Moyen/Difficile",
                "ingredients": [
                    {
                        "name": "Nom de l'ingrédient",
                        "quantity": "Quantité",
                        "unit": "Unité de mesure"
                    }
                ],
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Description de l'étape"
                    }
                ],
                "tips": ["Conseils pour la recette"]
            }
        ]
    }
}
```

## Intégration avec une application mobile

Pour intégrer cet agent dans votre application mobile, vous pouvez faire des appels API vers l'endpoint `/api/chat`. Assurez-vous d'inclure les headers CORS appropriés dans vos requêtes.

Exemple d'utilisation dans une application mobile :
```javascript
fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        message: "Nous sommes 4 et nous voulons manger un plat italien avec de la sauce tomate, du chocolat et de la mangue"
    })
})
.then(response => response.json())
.then(data => {
    switch(data.type) {
        case 'recipes':
            // Traiter les recettes
            console.log(data.data.recipes);
            break;
        case 'substitutions':
            // Traiter les substitutions
            console.log(data.data.substitutions);
            break;
        case 'analysis':
            // Traiter l'analyse
            console.log(data.data.analysis);
            break;
    }
});
``` #   s h o p y c h e f  
 