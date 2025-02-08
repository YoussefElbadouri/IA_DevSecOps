import json
import re
from dockerfile_parse import DockerfileParser

# balaye tous les configurations ---------------------------------------------------------------------
def check_compliance(dfp):
    """Vérifie toutes les conformités et non-conformités d'un Dockerfile."""

    compliance = {
        "Conforme": [],
        "Non Conforme": []
    }

    # ✅ Vérifier si l'image de base est optimisée
    if dfp.baseimage:
        if ":" not in dfp.baseimage or dfp.baseimage.endswith(":latest"):
            compliance["Non Conforme"].append(
                f"L'image `{dfp.baseimage}` utilise `:latest` ou ne spécifie pas de version.")
        else:
            compliance["Conforme"].append(f"L'image `{dfp.baseimage}` spécifie une version correcte.")

    # ✅ Vérifier si un utilisateur non-root est utilisé
    user_entries = [entry['value'] for entry in dfp.structure if entry['instruction'] == "USER"]
    if user_entries and user_entries[0] != "root":
        compliance["Conforme"].append(f"Utilisateur non-root détecté: {user_entries[0]}")
    else:
        compliance["Non Conforme"].append("L'utilisateur root est utilisé.")

    # ✅ Vérifier la présence de labels obligatoires
    required_labels = {"maintainer", "version", "description"}
    found_labels = {entry['value'].split("=")[0].strip().lower() for entry in dfp.structure if
                    entry['instruction'] == "LABEL"}
    missing_labels = required_labels - found_labels
    if missing_labels:
        compliance["Non Conforme"].append(f"Labels manquants : {', '.join(missing_labels)}")
    else:
        compliance["Conforme"].append("Tous les labels obligatoires sont présents.")

    # ✅ Vérifier si les ports sensibles sont exposés
    sensitive_ports = {22, 23, 3389, 1521, 3306, 5432, 8080, 8443, 6379, 9200}
    exposed_ports = [entry['value'] for entry in dfp.structure if entry['instruction'] == "EXPOSE"]
    if any(int(port) in sensitive_ports for ports in exposed_ports for port in ports.split()):
        compliance["Non Conforme"].append("Un port sensible est exposé.")
    else:
        compliance["Conforme"].append("Aucun port sensible n'est exposé.")

    # ✅ Vérifier la gestion des secrets dans ENV
    secret_keywords = ["password", "secret", "key", "token"]
    has_secrets = any(
        any(secret in entry['value'].lower() for secret in secret_keywords) for entry in dfp.structure if
        entry['instruction'] == "ENV")
    if has_secrets:
        compliance["Non Conforme"].append("Un secret a été trouvé dans ENV.")
    else:
        compliance["Conforme"].append("Aucun secret détecté dans ENV.")

    # ✅ Vérifier si le cache est nettoyé après `apt-get install`
    apt_cleaned = any(
        "apt-get install" in entry['value'] and "&& rm -rf /var/lib/apt/lists/*" in entry['value'] for entry in
        dfp.structure if entry['instruction'] == "RUN")
    if apt_cleaned:
        compliance["Conforme"].append("Le cache est bien nettoyé après `apt-get install`.")
    else:
        compliance["Non Conforme"].append("Le cache n'est pas nettoyé après `apt-get install`.")

    # ✅ Vérifier si le multi-stage build est utilisé
    from_entries = [entry['value'] for entry in dfp.structure if entry['instruction'] == "FROM"]
    if len(from_entries) > 1:
        compliance["Conforme"].append("Le multi-stage build est utilisé.")
    else:
        compliance["Non Conforme"].append("Le multi-stage build n'est pas utilisé.")

    # Enregistrer en format JSON
    with open("DockerFile_vulnerabilities.json", "w", encoding="utf-8") as json_file:
        json.dump(compliance, json_file, indent=4, ensure_ascii=False)
    print("✅ Analyse des des vulnérabilités terminée ! Les résultats sont enregistrés dans `DockerFile_vulnerabilities.json`.")

# analyse des infos de fichier dockerfile ---------------------------------------------

def extract_dockerfile_info(dfp):
    """
    Analyse un Dockerfile et extrait toutes les informations utiles :
    - Instructions utilisées
    - Sécurité
    - Bonnes pratiques
    - Versions
    - Analyse des labels, ports, dépendances, etc.
    """
    results = {
        "Instructions": {},
        "Sécurité": [],
        "Bonne Pratique": [],
        "Version": [],
        "Labels": {},
        "Ports Exposés": [],
        "Dépendances": [],
    }

    # Lire le Dockerfile


    # 🔹 1. Lister toutes les instructions utilisées
    for entry in dfp.structure:
        instr = entry['instruction']
        if instr not in results["Instructions"]:
            results["Instructions"][instr] = []
        results["Instructions"][instr].append(entry['value'])

    # 🔹 2. Vérifier l'utilisateur root
    if any(entry['instruction'] == "USER" and entry['value'].strip() == "root" for entry in dfp.structure):
        results["Sécurité"].append("L'utilisateur root est utilisé, ce qui est une faille de sécurité.")

    # 🔹 3. Vérifier les ports exposés
    sensitive_ports = {22, 23, 3389, 1521, 3306, 5432, 8080, 8443, 6379, 9200}
    for entry in dfp.structure:
        if entry['instruction'] == "EXPOSE":
            ports = entry['value'].split()
            results["Ports Exposés"].extend(ports)
            for port in ports:
                if port.isdigit() and int(port) in sensitive_ports:
                    results["Sécurité"].append(f"Port sensible exposé ({port}).")

    # 🔹 4. Vérifier les secrets dans ENV
    secret_keywords = ["password", "secret", "key", "token"]
    for entry in dfp.structure:
        if entry['instruction'] == "ENV":
            env_var = entry['value'].lower()
            if any(secret in env_var for secret in secret_keywords):
                results["Sécurité"].append(f"Secret détecté dans ENV : {entry['value']}.")

    # 🔹 5. Vérifier l'image utilisée
    if dfp.baseimage:
        results["Version"].append(f"Image utilisée : {dfp.baseimage}")
        if ":" not in dfp.baseimage:
            results["Version"].append(f"L'image `{dfp.baseimage}` ne spécifie pas de version.")
        if dfp.baseimage.endswith(":latest"):
            results["Version"].append(f"L'image `{dfp.baseimage}` utilise `:latest`, ce qui est déconseillé.")

    # 🔹 6. Vérifier l'installation des dépendances
    for entry in dfp.structure:
        if entry['instruction'] == "RUN":
            results["Dépendances"].append(entry['value'])
            if "apt-get install" in entry['value'] and "&& rm -rf /var/lib/apt/lists/*" not in entry['value']:
                results["Bonne Pratique"].append("`apt-get install` est utilisé sans suppression du cache.")

    # 🔹 7. Vérifier les LABELs
    required_labels = ["maintainer", "version", "description"]
    found_labels = set()
    for entry in dfp.structure:
        if entry['instruction'] == "LABEL":
            label_content = entry['value']
            key_value_pairs = label_content.split("=")
            if len(key_value_pairs) == 2:
                key, value = key_value_pairs[0].strip(), key_value_pairs[1].strip()
                results["Labels"][key] = value
                found_labels.add(key.lower())

                # Vérifier l'email du maintainer
                if key.lower() == "maintainer" and not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                    results["Bonne Pratique"].append("L'email dans le LABEL maintainer est invalide.")

    # Vérifier les labels manquants
    missing_labels = set(required_labels) - found_labels
    if missing_labels:
        results["Bonne Pratique"].append(f"Labels manquants : {', '.join(missing_labels)}.")

    #  Vérifier l'utilisation de COPY vs ADD
    for entry in dfp.structure:
        if entry['instruction'] == "ADD":
            results["Bonne Pratique"].append("Utilisation de `ADD` au lieu de `COPY`.")

    #  Enregistrer les résultats en JSON
    with open("dockerfile_infos.json", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4, ensure_ascii=False)

    print("✅ Analyse terminée ! Les résultats sont enregistrés dans `dockerfile_infos.json`.")


def analyze_dockerfile(dockerfile_path):
    with open(dockerfile_path, 'r') as f:
        content = f.read()

    dfp = DockerfileParser()
    dfp.content = content
    extract_dockerfile_info(dfp)
    check_compliance(dfp)


# Exécuter le script sur un Dockerfile
path = "./configurations/Dockerfile"
analyze_dockerfile(path)

