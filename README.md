# TalentMatch

1.  **Créer un environnement virtuel Django :**
    ```
      -m venv env
    ```
2.  **Activer le environnement virtuel Django :**
    ```
    env\Scripts\activate
    ```
3.  **Installer dépendances si ce n'est pas encore fait :**
    ```
    pip install -r  requirements.txt
    ```
    ## Si vous avez de nouvelles dépendances,ajouter dans requirements.txt manuellement !!!
4.  **Installer dépendances si ce n'est pas encore fait :**
    Créer un .env et suiver l'exemple dans .env.example
5.  ## Lancer le serveur de développement

    Pour exécuter le serveur de développement Django, ouvrez votre terminal dans le répertoire racine du projet (celui qui contient le fichier `manage.py`) et exécutez la commande suivante :

    ```
    uvicorn main:app  --port 8001

    Demarage sans devoir a redemareer a chaque modif 

    uvicorn main:app --reload --port 8001

    ```

  ## desactiver l'environement python
    ```
    env\Scripts\deactivate
    ```
      ## Pour plus de tutoriel sur FastAPI et sa structure clicker sur le lien si dessous
  ⚡**N'effacez aucun __init__.py**

   https://fastapi.tiangolo.com/


   curl --location 'localhost:8001/api/matching/cv/68aa9e2eaf25adbc6b9aad30'

   curl --location 'localhost:8001/api/matching/offre/68aad899a517b82777d29282' \--data ''