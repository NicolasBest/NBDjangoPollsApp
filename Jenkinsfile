pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        SITE_NAME    = "nbdjangopollsapp"
        PROJECT_DIR  = "/var/www/nbdjangopollsapp"
        VENV_DIR     = "/var/www/nbdjangopollsapp/venv"
        NGINX_CONF   = "/etc/nginx/sites-available/nbdjangopollsapp"
        REPO_URL     = "https://github.com/NicolasBest/NBDjangoPollsApp.git"
        BRANCH_NAME  = "main"
        DJANGO_PORT  = "8000"
    }

    options {
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                git url: "${REPO_URL}", branch: "${BRANCH_NAME}"
            }
        }

        stage('Verify Project Files') {
            steps {
                sh '''
                    set -e
                    echo "Checking required Django project files..."

                    test -f manage.py
                    test -f requirements.txt
                    test -d mysite
                    test -d polls

                    echo "Required files found."
                    ls -la
                '''
            }
        }

        stage('Install Packages if Missing') {
            steps {
                sh '''
                    set -e

                    sudo apt update

                    if ! command -v python3 >/dev/null 2>&1; then
                        sudo apt install -y python3
                    fi

                    if ! command -v pip3 >/dev/null 2>&1; then
                        sudo apt install -y python3-pip
                    fi

                    if ! command -v python3 -m venv --help >/dev/null 2>&1; then
                        sudo apt install -y python3-venv
                    fi

                    if ! command -v nginx >/dev/null 2>&1; then
                        sudo apt install -y nginx
                    fi

                    if ! command -v rsync >/dev/null 2>&1; then
                        sudo apt install -y rsync
                    fi
                '''
            }
        }

        stage('Create Project Directory') {
            steps {
                sh '''
                    set -e
                    sudo mkdir -p "$PROJECT_DIR"
                    sudo chown -R jenkins:jenkins "$PROJECT_DIR"
                '''
            }
        }

        stage('Deploy Project Files') {
            steps {
                sh '''
                    set -e

                    echo "Cleaning old deployed files..."
                    rm -rf "$PROJECT_DIR"/*

                    echo "Copying Django project files..."
                    rsync -av --delete \
                        --exclude='.git' \
                        --exclude='venv' \
                        --exclude='__pycache__' \
                        --exclude='Jenkinsfile' \
                        --exclude='Jenkinsfile.txt' \
                        ./ "$PROJECT_DIR"/

                    echo "Deployed files:"
                    ls -la "$PROJECT_DIR"
                '''
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                sh '''
                    set -e
                    cd "$PROJECT_DIR"

                    python3 -m venv "$VENV_DIR"
                    . "$VENV_DIR/bin/activate"

                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install gunicorn
                '''
            }
        }

        stage('Run Django Migrations') {
            steps {
                sh '''
                    set -e
                    cd "$PROJECT_DIR"

                    . "$VENV_DIR/bin/activate"
                    python manage.py migrate
                '''
            }
        }

        stage('Collect Static Files') {
            steps {
                sh '''
                    set -e
                    cd "$PROJECT_DIR"

                    . "$VENV_DIR/bin/activate"
                    python manage.py collectstatic --noinput || true
                '''
            }
        }

        stage('Create Systemd Service') {
            steps {
                sh '''
                    set -e

                    sudo tee /etc/systemd/system/${SITE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Gunicorn for ${SITE_NAME}
After=network.target

[Service]
User=jenkins
Group=jenkins
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/gunicorn --bind 127.0.0.1:${DJANGO_PORT} mysite.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

                    sudo systemctl daemon-reload
                    sudo systemctl enable ${SITE_NAME}
                    sudo systemctl restart ${SITE_NAME}
                    sudo systemctl status ${SITE_NAME} --no-pager
                '''
            }
        }

        stage('Configure Nginx') {
            steps {
                sh '''
                    set -e

                    sudo tee "$NGINX_CONF" > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location /static/ {
        alias ${PROJECT_DIR}/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:${DJANGO_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

                    sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/${SITE_NAME}
                    sudo rm -f /etc/nginx/sites-enabled/default

                    sudo nginx -t
                    sudo systemctl enable nginx
                    sudo systemctl restart nginx
                    sudo systemctl status nginx --no-pager
                '''
            }
        }

        stage('Test Website Locally') {
            steps {
                sh '''
                    set -e
                    curl -I http://localhost
                '''
            }
        }
    }

    post {
        success {
            echo 'Django deployment successful.'
            echo 'Open your EC2 public IP in a browser to view the site.'
        }
        failure {
            echo 'Deployment failed. Check the Jenkins console output.'
        }
    }
}