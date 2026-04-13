pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up virtual environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run migrations') {
            steps {
                sh '''
                . venv/bin/activate
                python manage.py migrate
                '''
            }
        }

        stage('Start Django server') {
            steps {
                sh '''
                pkill -f "manage.py runserver" || true
                export BUILD_ID=dontKillMe
                nohup bash -c ". venv/bin/activate && python manage.py runserver 0.0.0.0:8000" > django.log 2>&1 &
                sleep 5
                '''
            }
        }
    }
}
