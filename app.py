from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
)
import psycopg2
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# Vérification de la clé secrète JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
if not app.config["JWT_SECRET_KEY"]:
    raise RuntimeError("Erreur : JWT_SECRET_KEY n'est pas défini dans le fichier .env")

# Configuration du JWT
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # Token expire en 1 heure
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 86400  # Refresh token expire en 24 heures
jwt = JWTManager(app)


# Connexion à PostgreSQL
def get_db_connection():
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
    except psycopg2.Error as e:
        print("❌ Erreur de connexion à la base de données :", e)
        return None


@app.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    return jsonify({
        "policies": 12,
        "alerts": 5,
        "securityScore": 85
    }), 200


# Route pour l'inscription
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name, email, password = data.get("name"), data.get("email"), data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Tous les champs sont obligatoires"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Impossible de se connecter à la base de données"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id",
                        (name, email, hashed_password))
            user_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({"message": "Inscription réussie", "user_id": user_id}), 201
    except psycopg2.Error as e:
        print("❌ Erreur lors de l'inscription :", e)
        return jsonify({"error": "Erreur lors de l'inscription"}), 500
    finally:
        conn.close()


# Route pour la connexion
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email, password = data.get("email"), data.get("password")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erreur de connexion à la base de données"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

            if user and bcrypt.check_password_hash(user[3], password):
                access_token = create_access_token(identity=user[0])
                refresh_token = create_refresh_token(identity=user[0])
                return jsonify({
                    "message": "Connexion réussie",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"id": user[0], "name": user[1], "email": user[2]}
                })
            else:
                return jsonify({"error": "Identifiants incorrects"}), 401
    except psycopg2.Error as e:
        print("❌ Erreur lors de la connexion :", e)
        return jsonify({"error": "Erreur lors de la connexion"}), 500
    finally:
        conn.close()


# Route pour rafraîchir le token JWT
@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": new_access_token})


# Route protégée (Dashboard)
@app.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    return jsonify({"message": f"Bienvenue, utilisateur {user_id} !"})


# Route pour récupérer les risques de sécurité
@app.route("/risks", methods=["GET"])
@jwt_required()
def get_risks():
    # 🔥 Données statiques pour une démonstration
    risks = [
        {"name": "Injection SQL", "level": 85},
        {"name": "Cross-Site Scripting (XSS)", "level": 70},
        {"name": "Fuite de données sensibles", "level": 90},
        {"name": "Attaque Man-in-the-Middle (MITM)", "level": 60},
        {"name": "Exploitation de vulnérabilités Zero-Day", "level": 95},
    ]

    return jsonify(risks), 200


# Lancer le serveur Flask
if __name__ == "__main__":
    app.run(debug=True, port=5000)
