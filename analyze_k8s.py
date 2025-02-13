import os
import json
import sys
import yaml
import re


def clean_repo_url():
    """ Nettoie l'URL du dépôt GitHub Et chercher le nom de projet  """
    repo_url = sys.argv[1]
    repo_url = repo_url.rstrip("/")
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]

    repo_name = repo_url.split("/")[-1]
    global OUTPUT_DIR
    global KUBERNETES_PATH
    OUTPUT_DIR = os.path.join("results/", repo_name)
    KUBERNETES_PATH = os.path.join("configurations/", repo_name)


# L'ajout de nom_de_projet dans le result dossier
clean_repo_url()

INFO_DIR = os.path.join(OUTPUT_DIR, "infos")
VULNERABILITY_DIR = os.path.join(OUTPUT_DIR, "vulnerabilites_analysis")


def ensure_directories():
    """Crée les dossiers nécessaires si non existants."""
    os.makedirs(INFO_DIR, exist_ok=True)
    os.makedirs(VULNERABILITY_DIR, exist_ok=True)


def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None


def parse_yaml(file_content):
    try:
        return list(yaml.safe_load_all(file_content))
    except:
        return []

def extract_yaml_info(yaml_data, file_name):
    if not isinstance(yaml_data, dict):
        return None

    extracted_info = {"fichier :": file_name, "informations extractées :": {
        "API Versions Utilisées": yaml_data.get("apiVersion", "Non spécifié"),
        "Types d'objets Kubernetes": yaml_data.get("kind", "Non spécifié"),
        "Nom de la ressource": yaml_data.get("metadata", {}).get("name", "Non spécifié"),
        "Namespace": yaml_data.get("metadata", {}).get("namespace", "default"),
        "Ports exposés": yaml_data.get("spec", {}).get("ports", "Non spécifié"),
        "Variables d'environnement": yaml_data.get("spec", {}).get("env", "Non spécifié"),
        "Secrets": yaml_data.get("spec", {}).get("secrets", "Non spécifié"),
        "Utilisation des privilèges": yaml_data.get("spec", {}).get("securityContext", {}).get("privileged","Non spécifié"),
        "Élévation de privilèges": yaml_data.get("spec", {}).get("securityContext", {}).get("allowPrivilegeEscalation", "Non spécifié"),
    }}
    return extracted_info


def detect_vulnerabilities(yaml_data, file_name):
    vulnerabilities = set()
    if not yaml_data:
        return list(vulnerabilities)

    if "spec" in yaml_data and "containers" in yaml_data["spec"]:
        for container in yaml_data["spec"]["containers"]:
            if "image" in container and ":latest" in container["image"]:
                vulnerabilities.add("⚠️ Utilisation de l'image 'latest', risque de mise à jour instable.")
            if "securityContext" not in container:
                vulnerabilities.add("⚠️ Absence de securityContext, manque de restrictions de sécurité.")
            if container.get("securityContext", {}).get("privileged", False):
                vulnerabilities.add("⚠️ Conteneur en mode privilégié, risque élevé de compromission.")
            if container.get("securityContext", {}).get("allowPrivilegeEscalation", True):
                vulnerabilities.add("⚠️ allowPrivilegeEscalation activé, risque d'élévation de privilèges.")
            if container.get("securityContext", {}).get("runAsUser", 0) == 0:
                vulnerabilities.add("⚠️ Le conteneur s'exécute en tant que root, risque élevé.")
            if not container.get("securityContext", {}).get("readOnlyRootFilesystem", False):
                vulnerabilities.add(
                    "⚠️ Le système de fichiers n'est pas en lecture seule, risque de modification malveillante.")

    if "networkPolicy" not in yaml_data:
        vulnerabilities.add("⚠️ Aucune NetworkPolicy définie, risque de mouvements latéraux non contrôlés.")

    if yaml_data.get("spec", {}).get("secrets", "Non spécifié") != "Non spécifié":
        vulnerabilities.add("⚠️ Présence de secrets potentiellement exposés.")

    return [{"fichier": file_name, "vulnérabilités": list(vulnerabilities)}]


def detect_exposed_credentials(file_content):
    issues = set()
    if re.search(r'AKIA[0-9A-Z]{16}', file_content):
        issues.add("⚠️ Clé AWS Access Key trouvée en dur.")
    if re.search(r'aws_secret_access_key\s*=\s*".{40}"', file_content):
        issues.add("⚠️ Clé AWS Secret Key trouvée en dur.")
    return list(issues)


def generate_reports(extracted_data, vulnerability_report):
    # Enregistrement des résultats
    with open(os.path.join(INFO_DIR, "yaml_extraction.json"), "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, indent=4, ensure_ascii=False)

    print("📄 Extraction des informations terminée pour les fichiers kuberntes !")
    # Enregistrement des résultats
    with open(os.path.join(VULNERABILITY_DIR, "yaml_vulnerabilities.json"), "w", encoding="utf-8") as json_file:
        json.dump(vulnerability_report, json_file, indent=4, ensure_ascii=False)

    print("📄 Analyse des vulnérabilités terminée pour les fichiers kuberntes !")


def analyze_all_yaml_files():
    extracted_data = []
    vulnerability_report = []
    processed_files = set()
    for root, _, files in os.walk(KUBERNETES_PATH):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                ensure_directories()
                file_path = os.path.join(root, file)
                if file_path in processed_files:
                    continue
                processed_files.add(file_path)
                file_content = read_file(file_path)
                if not file_content:
                    print(f"❌ Impossible de lire le fichier : {file_path}")
                    continue
                yaml_content = parse_yaml(file_content)
                for doc in yaml_content:
                    if doc:
                        extracted_data.append(extract_yaml_info(doc, file))
                        vulnerability_report.extend(detect_vulnerabilities(doc, file))
            else:
                print("❌ Aucun fichier YAML trouvé dans configurations/  .")
    generate_reports(extracted_data, vulnerability_report)


if __name__ == "__main__":
    analyze_all_yaml_files()
