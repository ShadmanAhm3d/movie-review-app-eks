pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        AWS_REGION = "ap-south-1"
        ACCOUNT_ID = "715860912025"

        // Correct ECR repo names
        BACKEND_REPO = "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/movie-backend"
        FRONTEND_REPO = "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/movie-frontend"
    }

    stages {

        stage('Login to ECR') {
            steps {
                sh '''
                aws ecr get-login-password --region ${AWS_REGION} | \
                docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                '''
            }
        }

        stage('Build Backend Image') {
            steps {
                sh '''
                docker build -t movie-backend:latest -f backend/Dockerfile .
                docker tag movie-backend:latest ${BACKEND_REPO}:latest
                '''
            }
        }

        stage('Push Backend Image') {
            steps {
                sh '''
                docker push ${BACKEND_REPO}:latest
                '''
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh '''
                docker build -t movie-frontend:latest -f frontend/Dockerfile .
                docker tag movie-frontend:latest ${FRONTEND_REPO}:latest
                '''
            }
        }

        stage('Push Frontend Image') {
            steps {
                sh '''
                docker push ${FRONTEND_REPO}:latest
                '''
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh '''
                aws eks update-kubeconfig --name movie-review --region ${AWS_REGION}

                kubectl apply -f eks-manifests/eks-maria-backend.yaml
                kubectl apply -f eks-manifests/movie-review-frontend.yaml

                kubectl rollout restart deployment movie-review-backend
                kubectl rollout restart deployment movie-review-frontend
                '''
            }
        }
    }
}

