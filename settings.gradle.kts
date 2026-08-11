pluginManagement {
    repositories {
        maven { 
            url = uri("http://localhost:8080/google")
            isAllowInsecureProtocol = true
        }
        maven { 
            url = uri("http://localhost:8080/central")
            isAllowInsecureProtocol = true
        }
        maven { 
            url = uri("http://localhost:8080/plugins")
            isAllowInsecureProtocol = true
        }
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        maven { 
            url = uri("http://localhost:8080/google")
            isAllowInsecureProtocol = true
        }
        maven { 
            url = uri("http://localhost:8080/central")
            isAllowInsecureProtocol = true
        }
        maven { 
            url = uri("http://localhost:8080/plugins")
            isAllowInsecureProtocol = true
        }
        google()
        mavenCentral()
    }
}
rootProject.name = "VerdisWallet"
include(":app")
