pipeline {
    agent any

    environment {
        PYTHON_VENV = "/var/jenkins_home/venv"
        GITHUB_REPO_URL = "https://github.com/Mrbiboy/dev.git"
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
                echo "📥 Clonage du dépôt contenant les scripts..."
                sh '''
                    #!/bin/bash
                    rm -rf dev
                    git clone ${env.GITHUB_REPO_URL} dev
                    cd dev
                    git fetch origin
                    git checkout main  # ou la branche que tu veux
                    git pull origin main
                '''
                echo "📂 Affichage du contenu du dépôt après clonage"
                sh 'ls -R dev/IA_DevSecOps'
            }
        }

        stage('Run Security Scan') {
            steps {
                echo "🚀 Lancement de l'extraction et de l'analyse..."
                sh '''
                    . $PYTHON_VENV/bin/activate
                    cd dev/IA_DevSecOps
                    python3 process_repo.py
                '''
            }
        }

        stage('Check JSON Reports') {
            steps {
                echo "📄 Vérification du contenu des fichiers JSON"
                sh '''
                    ls -l dev/IA_DevSecOps/configurations/*.json || echo "❌ Aucun fichier JSON trouvé !"
                '''
            }
        }

        stage('Archive Reports') {
            steps {
                echo "📦 Archivage des rapports JSON..."
                archiveArtifacts artifacts: 'dev/IA_DevSecOps/configurations/*.json', fingerprint: true
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
