// =============================================================
//  Pipeline de Integracao Continua — task2-financeiro
//
//  Fluxo (fases D, E, F, G da Tarefa Final):
//    Testes Automatizados  -> roda os 22 testes e publica estatisticas
//    Qualidade de Codigo   -> flake8; qualquer violacao falha a build
//    Build                 -> imagens versionadas da app e do banco
//    Deploy Homologacao    -> atualiza o ambiente de Homologacao
//    Aprovacao             -> liberacao manual para Producao
//    Deploy Producao       -> atualiza o ambiente de Producao
//
//  Roda no proprio container do Jenkins, que possui o Docker CLI e
//  acesso ao socket do Docker da VM.
// =============================================================
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        APP_VERSION = "b${BUILD_NUMBER}"   // versao da build = tag das imagens
        APP_IMAGE   = "task2-financeiro"
        DB_IMAGE    = "task2-flyway"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Testes Automatizados') {
            steps {
                // A imagem da app e construida aqui e reutilizada nos estagios
                // seguintes (testes, qualidade e deploy usam a mesma versao).
                sh 'docker build -t ${APP_IMAGE}:${APP_VERSION} ./app'
                sh '''
                    set +e
                    docker rm -f task2-tests-${BUILD_NUMBER} >/dev/null 2>&1
                    docker run --name task2-tests-${BUILD_NUMBER} \
                        ${APP_IMAGE}:${APP_VERSION} \
                        python -m pytest tests/ -v --junitxml=/tmp/report.xml
                    CODE=$?
                    docker cp task2-tests-${BUILD_NUMBER}:/tmp/report.xml report.xml
                    docker rm -f task2-tests-${BUILD_NUMBER} >/dev/null 2>&1
                    exit $CODE
                '''
            }
            post {
                always {
                    // Estatisticas de execucao dos testes (passou / falhou / tempo).
                    junit 'report.xml'
                }
            }
        }

        stage('Qualidade de Codigo') {
            steps {
                // flake8 le o app/.flake8; qualquer violacao encerra a build.
                sh 'docker run --rm ${APP_IMAGE}:${APP_VERSION} python -m flake8 .'
            }
        }

        stage('Build') {
            steps {
                // Build oficial: imagem do banco versionada e tags de release.
                sh 'docker build -t ${DB_IMAGE}:${APP_VERSION} ./db'
                sh 'docker tag ${APP_IMAGE}:${APP_VERSION} ${APP_IMAGE}:latest'
                sh 'docker tag ${DB_IMAGE}:${APP_VERSION} ${DB_IMAGE}:latest'
            }
        }

        stage('Deploy Homologacao') {
            steps {
                sh 'APP_VERSION=${APP_VERSION} docker compose -f environments/homolog/docker-compose.yml up -d'
            }
        }

        stage('Aprovacao para Producao') {
            steps {
                input message: 'Versao validada em Homologacao. Promover para Producao?',
                      ok: 'Implantar em Producao'
            }
        }

        stage('Deploy Producao') {
            steps {
                sh 'APP_VERSION=${APP_VERSION} docker compose -f environments/prod/docker-compose.yml up -d'
            }
        }
    }

    post {
        success {
            echo "Pipeline concluido — versao ${APP_VERSION} implantada em Homologacao e Producao."
        }
        failure {
            echo "Pipeline falhou — verifique o estagio com erro acima."
        }
    }
}
