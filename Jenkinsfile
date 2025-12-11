pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        AWS_REGION = "ap-south-1"
        ACCOUNT_ID = "715860912025"
        BACKEND_REPO = "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/movie-review-backend"
        FRONTEND_REPO = "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/movie-review-frontend"
    }

    stages {

    //    stage('Checkout Code') {
     //       steps {
      //          git branch: 'master',
       //             credentialsId: 'git-ssh-key',
        //            url: 'git@github.com:ShadmanAhm3d/movie-review-app-eks.git'
         //   }
//        }

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

                # apply backend & DB changes
                kubectl apply -f eks-manifests/eks-maria-backend.yaml

                # apply frontend
                kubectl apply -f eks-manifests/movie-review-frontend.yaml

                # restart backend pod to pull new image
                kubectl rollout restart deployment movie-review-backend

                # restart frontend
                kubectl rollout restart deployment movie-review-frontend
                '''
            }
        }
    }
}

