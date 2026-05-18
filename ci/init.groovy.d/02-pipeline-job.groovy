// Cria o job 'task2-pipeline' na primeira inicializacao do Jenkins.
// Equivale a um job "Pipeline script from SCM" apontando para o
// Jenkinsfile na raiz do repositorio.
import jenkins.model.Jenkins

def jobName  = "task2-pipeline"
def instance = Jenkins.get()

// Idempotente: so cria se o job ainda nao existir.
if (instance.getItem(jobName) == null) {
    def configXml = '''<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>Pipeline de CI/CD da aplicacao task2-financeiro</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>https://github.com/JonathanGuil/task2-financeiro.git</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="empty-list"/>
      <extensions/>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>'''

    instance.createProjectFromXML(
        jobName, new ByteArrayInputStream(configXml.getBytes("UTF-8")))
    println "--> Job '${jobName}' criado."
}
