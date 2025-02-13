pipeline {
    agent any

    environment {
        PYTHON_VENV = "/var/jenkins_home/venv"
    }

    stages {
        stage('User Input') {
            steps {
                script {
                    env.GITHUB_REPO_URL = input(
                        message: '🔗 Entrez le lien du dépôt GitHub à scanner :',
                        ok: 'Lancer le Scan',
                        parameters: [
                            string(name: 'GITHUB_REPO_URL', defaultValue: 'https://github.com/Mrbiboy/dev.git', description: 'Lien du dépôt GitHub')
                        ]
                    )
                }
            }
        }

        stage('Checkout') {
            steps {
                echo "📥 Clonage du dépôt centralisé contenant les scripts..."
                sh '''
                    rm -rf dev
                    git clone https://github.com/YoussefElbadouri/IA_DevSecOps.git
                '''
                echo "📂 Affichage du contenu du dépôt après clonage"
                sh 'ls -R '
            }
        }

        stage('Run Security Scan') {
            steps {
                echo "🚀 Lancement de l'extraction et de l'analyse..."
                sh '''
                    . $PYTHON_VENV/bin/activate
                    python3 process_repo.py
                '''
            }
        }

        stage('Check JSON Reports') {
            steps {
                echo "📄 Vérification du contenu des fichiers JSON"
                sh '''
                    ls -l results/*/infos/*.json || echo "❌ Aucun fichier JSON trouvé !"
                '''
            }
        }

        stage('Archive Reports') {
            steps {
                echo "📦 Archivage des rapports JSON..."
                archiveArtifacts artifacts: 'results/*/infos/*.json', fingerprint: true
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline terminé avec succès !"
        }
        failure {
            echo "❌ Erreur dans le pipeline. Vérifiez les logs."
        }
    }
}
