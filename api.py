from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

# Initialisation de l'application FastAPI
app = FastAPI()

# Configuration de la base de donn\u00e9es MySQL
DB_CONFIG = {
    "host": "localhost",  # Exemple : serveur local
    "port": "3306",       # Port par d\u00e9faut de MySQL
    "user": "root",       # Exemple : utilisateur par d\u00e9faut
    "password": "",       # Remplacez par votre mot de passe
    "database": "ecole"
}

# Mod\u00e8le pour les entr\u00e9es
class Etudiant(BaseModel):
    nom: str
    prenom: str
    naissance: int
    photo: str

# Connexion \u00e0 la base de donn\u00e9es
def get_db_connection():
    try:
        connect = mysql.connector.connect(**DB_CONFIG)
        cursor = connect.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `classe` (
                `id` int NOT NULL AUTO_INCREMENT,
                `nom` varchar(250) NOT NULL,
                `prenom` varchar(250) NOT NULL,
                `naissance` int NOT NULL,
                `photo` varchar(250) NOT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
        """)
        cursor.close()
        return connect
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de connexion à la base de données : {e}")

# Endpoint : teste le d\u00e9marrage de l'API
@app.get("/")
def test_demarrage():
    return {"serveur": "démarré"}

# Endpoint : Liste de tous les \u00e9tudiants
@app.get("/etudiants")
def get_all_etudiants():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM classe")
    etudiants = cursor.fetchall()
    connection.close()
    return etudiants

# Endpoint : Ajout d'un nouvel \u00e9tudiant
@app.post("/etudiant")
def add_etudiant(etudiant: Etudiant):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO classe (nom, prenom, photo, naissance) VALUES (%s, %s, %s, %s)",
        (etudiant.nom, etudiant.prenom, etudiant.photo, etudiant.naissance)
    )
    connection.commit()
    new_id = cursor.lastrowid
    connection.close()
    return {"id": new_id, "message": "L'étudiant ajouté avec succés"}

# Endpoint : Supprimer un étudiant suivant son ID
@app.delete("/etudiant/{etudiant_id}")
def delete_etudiant(etudiant_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM classe WHERE id = %s", (etudiant_id,))
    connection.commit()
    affected_rows = cursor.rowcount
    connection.close()
    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="Etudiant non trouv\u00e9")
    return {"message": "Etudiant supprimé avec succés"}
