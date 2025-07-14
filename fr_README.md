# PatotIA - Assistant IA pour calculs et simulation 3D
### *Pour un aperçu plus complet de mon travail, visitez mon portfolio sur [imonge.es](https://imonge.es/perso_proyecto/1?lang=fr).*
## Instructions d'Installation
### Téléchargement du Modèle
1. Téléchargez le fichier de modèle (`.pth`) et son fichier de hachage correspondant (`.txt`) depuis la section **Releases**: [Robot_AI_Trained_Model](https://github.com/IsmaTIBU/PatotIA/releases/tag/Robot_AI_TrainedModel).
2. Placez les deux fichiers dans le dossier `Backend/models` du projet.
3. Pour vérifier que le modèle a été chargé correctement, exécutez `python verify_model` dans votre terminal.
### Étapes d'Exécution
Depuis la racine du répertoire cloné, exécutez ces commandes :
1. `pip install -r required.txt`
2. `cd .\Backend`
3. `python .\api.py`
## Sortie Attendue
Après avoir exécuté les commandes, vous devriez voir la sortie suivante dans votre terminal (cela peut prendre du temps) :
```
============================================================
🤖 ROBOT AI WEB SERVER
============================================================
Initializing Robot-AI ...
============================================================
Loading trained model...
✅ Model loaded and ready to use!
✅ AI ready!
============================================================
 * Serving Flask app 'api'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[Votre adresse IP]:5000
Press CTRL+C to quit
```
## Accès à l'Application
Vous pouvez accéder à l'application en :
1. Double-cliquant sur le fichier `index.html` dans le répertoire `Frontend`, ou
2. Visitant `http://127.0.0.1:5000` dans votre navigateur web préféré.
## Évolution du Projet
- Chemin de développement : Ollama + détection de motifs → FlanT5 → CodeT5
- Précision atteinte : 92.94% (sur 100 tests)
