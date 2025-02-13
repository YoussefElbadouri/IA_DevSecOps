import sys
import hcl2
import re
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def clean_repo_url():
    """ Nettoie l'URL du dépôt GitHub Et chercher le nom de projet  """
    repo_url = sys.argv[1]
    repo_url = repo_url.rstrip("/")
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]

    repo_name = repo_url.split("/")[-1]
    global OUTPUT_DIR
    global TERRAFORM_PATH
    OUTPUT_DIR = os.path.join("results/", repo_name)
    TERRAFORM_PATH = os.path.join("configurations/", repo_name)


# L'ajout de nom_de_projet dans le result dossier
clean_repo_url()
INFO_DIR = os.path.join(OUTPUT_DIR, "infos")
VULNERABILITY_DIR = os.path.join(OUTPUT_DIR, "vulnerabilites_analysis")


def ensure_directories():
    """Crée les dossiers nécessaires si non existants."""
    os.makedirs(INFO_DIR, exist_ok=True)
    os.makedirs(VULNERABILITY_DIR, exist_ok=True)


def get_terraform_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".tf")]


def load_terraform_config(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return hcl2.load(file)


def format_details(data):
    if isinstance(data, dict):
        return ", ".join([f"{key}: {value}" for key, value in data.items()])
    elif isinstance(data, list):
        return ", ".join([str(item) for item in data])
    return str(data)


def check_security_groups(terraform_config):
    issues, details = set(), set()
    for resource in terraform_config.get("resource", []):
        if "aws_security_group" in resource:
            for sg_name, sg_config in resource["aws_security_group"].items():
                for rule in sg_config.get("ingress", []):
                    detail = f"Security Group '{sg_name}' autorise {rule.get('from_port', 'Unknown')} à {rule.get('cidr_blocks', 'Unknown')}"
                    details.add(detail)
                    if "cidr_blocks" in rule and "0.0.0.0/0" in rule["cidr_blocks"]:
                        issues.add(f"⚠️ {sg_name} : Ouverture du port {rule['from_port']} à tout le monde.")
    return list(details), list(issues)


def check_iam_policies(terraform_config):
    issues, details = set(), set()
    for resource in terraform_config.get("resource", []):
        if "aws_iam_policy" in resource:
            for policy_name, policy_config in resource["aws_iam_policy"].items():
                formatted_policy = format_details(policy_config)
                details.add(f"Policy IAM '{policy_name}' - {formatted_policy}")
                if '"Action": "*"' in str(policy_config):
                    issues.add(f"⚠️ {policy_name} : Permission excessive (*).")
    return list(details), list(issues)


def check_s3_encryption(terraform_config):
    issues, details = set(), set()
    for resource in terraform_config.get("resource", []):
        if "aws_s3_bucket" in resource:
            for bucket_name, bucket_config in resource["aws_s3_bucket"].items():
                formatted_bucket = format_details(bucket_config)
                details.add(f"Bucket S3 '{bucket_name}' - {formatted_bucket}")
                if "server_side_encryption_configuration" not in bucket_config:
                    issues.add(f"⚠️ {bucket_name} : Pas de chiffrement activé.")
    return list(details), list(issues)


def check_vpc_isolation(terraform_config):
    issues, details = set(), set()
    for resource in terraform_config.get("resource", []):
        if "aws_subnet" in resource:
            for subnet_name, subnet_config in resource["aws_subnet"].items():
                formatted_subnet = format_details(subnet_config)
                details.add(f"Subnet '{subnet_name}' - {formatted_subnet}")
                if subnet_config.get("map_public_ip_on_launch", False):
                    issues.add(f"⚠️ {subnet_name} : Subnet public sans protection.")
    return list(details), list(issues)


def check_exposed_credentials(file_path):
    issues, details = set(), set()
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if re.search(r'AKIA[0-9A-Z]{16}', line):
                issues.add("⚠️ Clé AWS Access Key trouvée en dur.")
            if re.search(r'aws_secret_access_key\s*=\s*\".{40}\"', line):
                issues.add("⚠️ Clé AWS Secret Key trouvée en dur.")
            if "aws_access_key" in line or "aws_secret_key" in line:
                details.add(line.strip())
    return list(details), list(issues)


def check_logging(terraform_config):
    issues, details = set(), set()
    details.add("Vérification des services CloudTrail et CloudWatch.")
    if not any("aws_cloudtrail" in resource for resource in terraform_config.get("resource", [])):
        issues.add("⚠️ CloudTrail n'est pas activé.")
    return list(details), list(issues)


def save_report_pdf(report, filename):
    """Génère un rapport PDF structuré et lisible."""
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)

    y = 750
    c.drawString(100, y, "📄 Rapport d'Analyse Terraform")
    y -= 30  # Espacement avant la première section

    for category, issues in report.items():
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.darkblue)
        c.drawString(80, y, f"📌 {category}")
        y -= 20

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.black)
        if issues:
            for issue in issues:
                c.drawString(100, y, f"⚠️ {format_details(issue)}")
                y -= 15
        else:
            c.drawString(100, y, "✅ Aucun problème détecté.")
            y -= 15

        y -= 10  # Espacement entre les sections

    c.save()
    print(f" Rapport PDF généré : {filename}")


def save_report_json(report, filename, type):
    if type == "vul":
        # Enregistrement des résultats
        with open(os.path.join(VULNERABILITY_DIR, filename), "w", encoding="utf-8") as json_file:
            json.dump(report, json_file, indent=4, ensure_ascii=False)
        print("📄 Analyse des vulnérabilités terminée pour les fichiers terraforms  !")
    if type == "infos":
        # Enregistrement des résultats
        with open(os.path.join(INFO_DIR, filename), "w", encoding="utf-8") as json_file:
            json.dump(report, json_file, indent=4, ensure_ascii=False)
        print("📄 Analyse des vulnérabilités terminée pour les fichiers terraforms  !")


def run_analysis():
    terraform_files = get_terraform_files(TERRAFORM_PATH)
    full_report = {}
    vulnerability_report = {}

    for terraform_file in terraform_files:
        print(f"🔍 Analyse du fichier Terraform : {terraform_file}")
        terraform_config = load_terraform_config(terraform_file)

        checks = {
            "Security Groups": check_security_groups(terraform_config),
            "Permissions IAM": check_iam_policies(terraform_config),
            "Chiffrement S3": check_s3_encryption(terraform_config),
            "Isolation VPC": check_vpc_isolation(terraform_config),
            "Identifiants exposés": check_exposed_credentials(terraform_file),
            "Logs et Audit": check_logging(terraform_config)
        }

        for check_name, (details, issues) in checks.items():
            full_report.setdefault(check_name, set()).update(details)
            vulnerability_report.setdefault(check_name, set()).update(issues)

    for key in full_report:
        full_report[key] = list(full_report[key])
    for key in vulnerability_report:
        vulnerability_report[key] = list(vulnerability_report[key])

    save_report_json(full_report, "rapport_complet.json", "infos")
    save_report_pdf(full_report, "rapport_complet.pdf")
    save_report_json(vulnerability_report, "rapport_vulnerabilites.json", "vul")
    save_report_pdf(vulnerability_report, "rapport_vulnerabilites.pdf")


# Lancer l'analyse sur tous les fichiers  dans le dossier siblé
run_analysis()
