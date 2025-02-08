import hcl2
import re
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Chemin du fichier Terraform à analyser
terraform_file = "infra.tf"

def load_terraform_config(file_path):
    """Charge un fichier Terraform et retourne son contenu analysé."""
    with open(file_path, "r") as file:
        return hcl2.load(file)

def format_details(data):
    """Transforme un dictionnaire ou une liste en texte lisible."""
    if isinstance(data, dict):
        return ", ".join([f"{key}: {value}" for key, value in data.items()])
    elif isinstance(data, list):
        return ", ".join([str(item) for item in data])
    return str(data)

def check_security_groups(terraform_config):
    """Vérifie les ports ouverts dans les Security Groups AWS."""
    issues, details = [], []
    for resource in terraform_config.get("resource", []):
        if "aws_security_group" in resource:
            for sg_name, sg_config in resource["aws_security_group"].items():
                for rule in sg_config.get("ingress", []):
                    details.append(f"Security Group '{sg_name}' autorise {rule.get('from_port', 'Unknown')} à {rule.get('cidr_blocks', 'Unknown')}")
                    if "cidr_blocks" in rule and "0.0.0.0/0" in rule["cidr_blocks"]:
                        issues.append(f"⚠️ {sg_name} : Ouverture du port {rule['from_port']} à tout le monde.")
    return details, issues

def check_iam_policies(terraform_config):
    """Vérifie si des permissions IAM excessives sont utilisées."""
    issues, details = [], []
    for resource in terraform_config.get("resource", []):
        if "aws_iam_policy" in resource:
            for policy_name, policy_config in resource["aws_iam_policy"].items():
                formatted_policy = format_details(policy_config)
                details.append(f"Policy IAM '{policy_name}' - {formatted_policy}")
                if '"Action": "*"' in str(policy_config):
                    issues.append(f"⚠️ {policy_name} : Permission excessive (*).")
    return details, issues

def check_s3_encryption(terraform_config):
    """Vérifie si le chiffrement S3 est activé."""
    issues, details = [], []
    for resource in terraform_config.get("resource", []):
        if "aws_s3_bucket" in resource:
            for bucket_name, bucket_config in resource["aws_s3_bucket"].items():
                formatted_bucket = format_details(bucket_config)
                details.append(f"Bucket S3 '{bucket_name}' - {formatted_bucket}")
                if "server_side_encryption_configuration" not in bucket_config:
                    issues.append(f"⚠️ {bucket_name} : Pas de chiffrement activé.")
    return details, issues

def check_vpc_isolation(terraform_config):
    """Vérifie si des sous-réseaux sont publics sans passer par un NAT."""
    issues, details = [], []
    for resource in terraform_config.get("resource", []):
        if "aws_subnet" in resource:
            for subnet_name, subnet_config in resource["aws_subnet"].items():
                formatted_subnet = format_details(subnet_config)
                details.append(f"Subnet '{subnet_name}' - {formatted_subnet}")
                if subnet_config.get("map_public_ip_on_launch", False):
                    issues.append(f"⚠️ {subnet_name} : Subnet public sans protection.")
    return details, issues

def check_exposed_credentials(file_path):
    """Vérifie si des identifiants AWS sont exposés en dur."""
    issues, details = [], []
    with open(file_path, "r") as file:
        for line in file:
            if re.search(r'AKIA[0-9A-Z]{16}', line):
                issues.append("⚠️ Clé AWS Access Key trouvée en dur.")
            if re.search(r'aws_secret_access_key\s*=\s*\".{40}\"', line):
                issues.append("⚠️ Clé AWS Secret Key trouvée en dur.")

            # Ajouter uniquement les identifiants exposés dans le rapport détaillé
            if "aws_access_key" in line or "aws_secret_key" in line:
                details.append(line.strip())

    return details, issues

def check_logging(terraform_config):
    """Vérifie si CloudTrail ou CloudWatch est activé."""
    issues, details = [], []
    details.append("Vérification des services CloudTrail et CloudWatch.")
    if not any("aws_cloudtrail" in resource for resource in terraform_config.get("resource", [])):
        issues.append("⚠️ CloudTrail n'est pas activé.")
    return details, issues

def save_report_json(report, filename):
    """Sauvegarde le rapport au format JSON propre et structuré."""
    cleaned_report = {}

    for key, value in report.items():
        if key == "Identifiants exposés":
            # Ne garder que les informations essentielles
            cleaned_report[key] = [item for item in value if "aws_access_key" in item or "aws_secret_key" in item]
        else:
            cleaned_report[key] = [format_details(item) for item in value]

    # Écriture propre dans le fichier JSON avec encodage UTF-8
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(cleaned_report, file, indent=4, ensure_ascii=False)

    print(f"📄 Rapport JSON généré : {filename}")

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
    print(f"📄 Rapport PDF généré : {filename}")

def run_analysis(terraform_file):
    """Exécute l'analyse et génère deux rapports : complet et vulnérabilités."""
    print(f"🔍 Analyse du fichier Terraform : {terraform_file}")
    terraform_config = load_terraform_config(terraform_file)

    full_report = {}
    vulnerability_report = {}

    checks = {
        "Security Groups": check_security_groups(terraform_config),
        "Permissions IAM": check_iam_policies(terraform_config),
        "Chiffrement S3": check_s3_encryption(terraform_config),
        "Isolation VPC": check_vpc_isolation(terraform_config),
        "Identifiants exposés": check_exposed_credentials(terraform_file),
        "Logs et Audit": check_logging(terraform_config)
    }

    for check_name, (details, issues) in checks.items():
        full_report[check_name] = details
        if issues:
            vulnerability_report[check_name] = issues

    # Générer les rapports
    save_report_json(full_report, "rapport_complet.json")
    save_report_pdf(full_report, "rapport_complet.pdf")
    save_report_json(vulnerability_report, "rapport_vulnerabilites.json")
    save_report_pdf(vulnerability_report, "rapport_vulnerabilites.pdf")

# Lancer l'analyse
run_analysis(terraform_file)
