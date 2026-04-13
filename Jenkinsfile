pipeline {
    agent any

    environment {
        APP_DIR = '/opt/django-polls'
        SERVICE_NAME = 'django-polls'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify Project Files') {
            steps {
                sh '''
                set -e
                pwd
                ls -la
                test -f manage.py
                test -f requirements.txt
                test -d mysite
                test -d polls
                '''
            }
        }

        stage('Create Project Directory') {
            steps {
                sh '''
                set -e
                sudo mkdir -p $APP_DIR
                sudo chown -R jenkins:jenkins $APP_DIR
                '''
            }
        }

        stage('Deploy Project Files') {
            steps {
                sh '''
                set -e
                rm -rf $APP_DIR/*
                cp -r . $APP_DIR/
                cd $APP_DIR
                ls -la
                '''
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                sh '''
                set -e
                cd $APP_DIR
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Django Migrations') {
            steps {
                sh '''
                set -e
                cd $APP_DIR
                . venv/bin/activate
                python manage.py migrate
                '''
            }
        }

        stage('Collect Static Files') {
            steps {
                sh '''
                set -e
                cd $APP_DIR
                . venv/bin/activate
                python manage.py collectstatic --noinput || true
                '''
            }
        }

        stage('Create Systemd Service') {
            steps {
                sh '''
                set -e
                sudo bash -c 'cat > /etc/systemd/system/'"$SERVICE_NAME"'.service <<EOF
[Unit]
Description=Django Polls App
After=network.target

[Service]
User=jenkins
Group=jenkins
WorkingDirectory='"$APP_DIR"'
Environment="PATH='"$APP_DIR"'/venv/bin"
ExecStart='"$APP_DIR"'/venv/bin/python '"$APP_DIR"'/manage.py runserver 0.0.0.0:8000 --noreload
Restart=always

[Install]
WantedBy=multi-user.target
EOF'
                sudo systemctl daemon-reload
                sudo systemctl enable $SERVICE_NAME
                '''
            }
        }

        stage('Restart Django Service') {
            steps {
                sh '''
                set -e
                sudo systemctl restart $SERVICE_NAME
                sudo systemctl status $SERVICE_NAME --no-pager
                '''
            }
        }

        stage('Test Website Locally') {
            steps {
                sh '''
                set -e
                sleep 5
                curl -I http://127.0.0.1:8000/polls/ || true
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment completed successfully.'
        }
        failure {
            echo 'Deployment failed. Check the console output.'
        }
    }
}