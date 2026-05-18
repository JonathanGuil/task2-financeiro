// Cria o usuario administrador do Jenkins na primeira inicializacao.
// A senha vem da variavel de ambiente JENKINS_ADMIN_PASSWORD, gerada pelo
// setup-jenkins.sh e guardada em ci/.env (fora do versionamento).
import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy

def instance = Jenkins.get()

// Idempotente: so configura na primeira vez. Se o admin ja existe (boots
// seguintes), nao mexe — preserva alteracoes feitas pela interface.
if (!(instance.getSecurityRealm() instanceof HudsonPrivateSecurityRealm)) {
    def user = System.getenv("JENKINS_ADMIN_USER") ?: "admin"
    def pass = System.getenv("JENKINS_ADMIN_PASSWORD")

    if (pass == null || pass.trim().isEmpty()) {
        throw new RuntimeException(
            "JENKINS_ADMIN_PASSWORD nao definida — verifique o arquivo ci/.env")
    }

    def realm = new HudsonPrivateSecurityRealm(false)
    realm.createAccount(user, pass)
    instance.setSecurityRealm(realm)

    def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
    strategy.setAllowAnonymousRead(false)
    instance.setAuthorizationStrategy(strategy)

    instance.save()
    println "--> Usuario administrador '${user}' criado."
}
