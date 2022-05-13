def bucketName = [
        "master" : "use1-web-dev-gms-ppapp-instagram-lambda-s3",
        "staging": "use1-web-stg-gms-ppapp-instagram-lambda-s3",
        "dev"    : "use1-web-prod-gms-ppapp-instagram-lambda-s3"
]
def skipStep = (JOB_BASE_NAME != 'main' && JOB_BASE_NAME != 'staging') ? false : true
def check_sum = ""
def app_name = "lambda-instagram-token-refresh-${JOB_BASE_NAME}"
pipeline {
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', artifactNumToKeepStr: '5'))
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds abortPrevious: true
    }
    agent {
        ecs {
            inheritFrom 'ecs_slave_light'
        }
    }
    stages {
        stage('Install packages') {

            steps {
                echo 'Install required packages '
                doAddDependencies(["zip"])
                echo 'Done'
            }

        }

        stage('AWS upload to s3') {
            when {
                expression { skipStep }
            }
            steps {
                echo 'Upload to S3'
                doAssumeRoleDefault(awsAccNo[JOB_BASE_NAME], awsJenkinsRole, app_name, region)
                sh """
                    cd ../

                    zip -r lambda.zip Shure_lambda-instagram-token-refresh_${JOB_BASE_NAME}

                    aws s3 sync lambda.zip s3://${bucketName[JOB_BASE_NAME]} --delete --region=us-east-1
                """
                echo 'Done'
            }
        }
    }

    post {
        // Always runs. And it runs before any of the other post conditions.
        always {
            sendNotifications currentBuild.result
        }
    }
}