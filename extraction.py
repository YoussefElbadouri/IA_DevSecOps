import requests
import os
from dotenv import load_dotenv

# Charger les variables d’environnement (GITHUB_TOKEN)
load_dotenv()

# 🟢 Remplace ces valeurs par celles de ton dépôt GitHub
GITHUB_OWNER = "YoussefElbadouri"
GITHUB_REPO = "tet"
OUTPUT_DIR = "configurations"  # Dossier où seront enregistrés les fichiers

# Charger le Token GitHub depuis un fichier .env ou variable d'environnement
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Vérifier que le Token est bien défini
if not GITHUB_TOKEN:
    raise ValueError("❌ Aucun jeton GitHub trouvé ! Ajoutez-le dans un fichier .env sous 'GITHUB_TOKEN'.")

# Extensions des fichiers de configuration que nous voulons extraire
TARGET_EXTENSIONS = [".tf", "Dockerfile", ".yaml", ".yml"]


def get_github_files(repo_owner, repo_name, path=""):
    """Récupère la liste des fichiers dans un dépôt GitHub privé en utilisant un Token."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"⚠️ Erreur de récupération ({response.status_code}) : {response.text}")
        return []


def download_file(file_url, output_path):
    """Télécharge un fichier depuis GitHub et l'enregistre localement."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(file_url, headers=headers)

    if response.status_code == 200:
        with open(output_path, "wb") as file:
            file.write(response.content)
        print(f"✅ Fichier téléchargé : {output_path}")
    else:
        print(f"⚠️ Impossible de télécharger {file_url}")


def extract_config_files(repo_owner, repo_name, path=""):
    """Télécharge les fichiers Terraform, Dockerfile et Kubernetes YAML depuis un dépôt privé GitHub."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = get_github_files(repo_owner, repo_name, path)

    if not files:
        print("❌ Aucun fichier trouvé.")
        return

    for file in files:
        file_name = file["name"]
        file_url = file.get("download_url")  # Certains fichiers peuvent ne pas avoir d'URL

        if not file_url:
            continue  # Ignore les dossiers et les fichiers non téléchargeables

        if any(file_name.endswith(ext) or file_name in TARGET_EXTENSIONS for ext in TARGET_EXTENSIONS):
            output_path = os.path.join(OUTPUT_DIR, file_name)
            download_file(file_url, output_path)


# 🟢 Exécution du script avec ton dépôt GitHub Privé
extract_config_files(GITHUB_OWNER, GITHUB_REPO)
