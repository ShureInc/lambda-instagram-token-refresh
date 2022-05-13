def bucketName = [
        "master" : "use1-web-prod-gms-ppapp-instagram-lambda-s3",
        "staging": "use1-web-stg-gms-ppapp-instagram-lambda-s3",
        "dev"    : "use1-web-dev-gms-ppapp-instagram-lambda-s3"
]
def awsAccNo = [
        "master" : "908685898936",
        "staging": "142316270592",
        "dev"    : "625998479255"
]
def awsRegion = [
        "master" : "us-east-1",
        "staging": "us-east-1",
        "dev"    : "us-east-1"
]

def region = awsRegion[JOB_BASE_NAME]
def skipStep = (JOB_BASE_NAME != 'main' && JOB_BASE_NAME != 'staging' && JOB_BASE_NAME != 'dev') ? false : true
def check_sum = ""
def app_name = "lambda-instagram-token-refresh-${JOB_BASE_NAME}"
def awsJenkinsRole = "shure-gms-jenkins-role"
pipeline {
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', artifactNumToKeepStr: '5'))
        timeout(time: 15, unit: 'MINUTES')
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
                    rm -rf .git
                    zip -r lambda.zip .
                    aws s3 cp lambda.zip s3://${bucketName[JOB_BASE_NAME]}/lambda.zip --region=${region}
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