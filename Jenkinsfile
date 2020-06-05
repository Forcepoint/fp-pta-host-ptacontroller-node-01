pipeline {
    agent {
        label 'pta-controller'
    }
    triggers {
        // Run between 10 PM and midnight on Saturdays.
        cron('H 20-21/2 * * 6')
    }
    options {
        disableConcurrentBuilds()
    }
    //environment {
    // Uncomment TF_LOG if you're trying to debug a problem with Terraform.
    // TF_LOG = "trace"
    //}
    parameters {
        booleanParam(name: "Terraform_Init_Local", defaultValue: false, description: 'Perform a terraform init with the already downloaded plugins in /usr/lib/custom-terraform-plugins (i.e. Local) or download them anew from the internet (i.e. External).')
        booleanParam(name: "Terraform_Taint", defaultValue: false, description: 'Perform a terraform taint on the module\'s vsphere_virtual_machine.vm. See https://www.terraform.io/docs/commands/taint.html')
        booleanParam(name: "Terraform_Untaint", defaultValue: false, description: 'Perform a terraform untaint on the module\'s vsphere_virtual_machine.vm.')
        choice(name: "Terraform_Module", choices: 'PTAPacker', description: 'The name of the module to perform the terraform taint or untaint on.')
        booleanParam(name: "Terraform_Apply", defaultValue: false, description: 'Perform a terraform apply.')
        booleanParam(name: 'Terraform_Verify', defaultValue: true, description: 'Before the Terraform plan is applied, it is wise to verify the plan manually. If you do not desire to do so, you can skip the verify step.')
        booleanParam(name: "Ansible", defaultValue: true, description: 'Run the ansible playbook.')
    }
    stages {
        stage('Terraform Init Local') {
            when {
                expression { params.Terraform_Init_Local }
            }
            steps {
                withCredentials([
                        usernamePassword(credentialsId: 'terraform-vsphere', usernameVariable: 'TF_VAR_vsphere_user', passwordVariable: 'TF_VAR_vsphere_password'),
                        usernamePassword(credentialsId: 'slcartifactory', usernameVariable: 'ARTIFACTORY_USERNAME', passwordVariable: 'ARTIFACTORY_PASSWORD')]) {
                    sh 'terraform init -no-color -upgrade -plugin-dir=/usr/lib/custom-terraform-plugins'
                }
            }
        }
        stage('Terraform Init External') {
            when {
                expression { ! params.Terraform_Init_Local }
            }
            steps {
                withCredentials([
                        usernamePassword(credentialsId: 'terraform-vsphere', usernameVariable: 'TF_VAR_vsphere_user', passwordVariable: 'TF_VAR_vsphere_password'),
                        usernamePassword(credentialsId: 'slcartifactory', usernameVariable: 'ARTIFACTORY_USERNAME', passwordVariable: 'ARTIFACTORY_PASSWORD')]) {
                    sh 'terraform init -no-color -upgrade'
                }
            }
        }
        stage('Terraform Taint') {
            when {
                expression { params.Terraform_Taint }
            }
            steps {
                withCredentials([
                        usernamePassword(credentialsId: 'terraform-vsphere', usernameVariable: 'TF_VAR_vsphere_user', passwordVariable: 'TF_VAR_vsphere_password'),
                        usernamePassword(credentialsId: 'slcartifactory', usernameVariable: 'ARTIFACTORY_USERNAME', passwordVariable: 'ARTIFACTORY_PASSWORD')]) {
                    sh "terraform taint -no-color module.${params.Terraform_Module}.vsphere_virtual_machine.vm"
                }
            }
        }
        stage('Terraform Untaint') {
            when {
                expression { params.Terraform_Untaint }
            }
            steps {
                withCredentials([
                        usernamePassword(credentialsId: 'terraform-vsphere', usernameVariable: 'TF_VAR_vsphere_user', passwordVariable: 'TF_VAR_vsphere_password'),
                        usernamePassword(credentialsId: 'slcartifactory', usernameVariable: 'ARTIFACTORY_USERNAME', passwordVariable: 'ARTIFACTORY_PASSWORD')]) {
                    sh "terraform untaint -no-color module.${params.Terraform_Module}.vsphere_virtual_machine.vm"
                }
            }
        }
        stage('Terraform PVA') {
            when {
                expression { params.Terraform_Apply }
            }
            stages {
                stage('Terraform Plan') {
                    steps {
                        withCredentials([
                                usernamePassword(credentialsId: 'terraform-vsphere', usernameVariable: 'TF_VAR_vsphere_user', passwordVariable: 'TF_VAR_vsphere_password'),
                                usernamePassword(credentialsId: 'slcartifactory', usernameVariable: 'ARTIFACTORY_USERNAME', passwordVariable: 'ARTIFACTORY_PASSWORD')]) {
                            sh 'terraform plan -no-color'
                        }
                    }
                }
                stage('Terraform Verify') {
                    when {
                        expression { params.Terraform_Verify }
                    }
                    steps {
                        input 'Are you sure you want to continue with the Terraform Apply?'
                    }
                }
                stage('Terraform Apply') {
                    steps {
                        withCredentials([
                                usernamePassword(credentialsId: 'terraform-vsphere', usernameVariable: 'TF_VAR_vsphere_user', passwordVariable: 'TF_VAR_vsphere_password'),
                                usernamePassword(credentialsId: 'slcartifactory', usernameVariable: 'ARTIFACTORY_USERNAME', passwordVariable: 'ARTIFACTORY_PASSWORD')]) {
                            sh 'terraform apply -no-color -auto-approve'
                        }
                    }
                }
            }
        }
        stage('Ansible') {
            when {
                expression { params.Ansible }
            }
            steps {
                sh '''
                    virtualenv virt_ansible
                    source virt_ansible/bin/activate
                    pip install -r requirements.txt
                    ansible-galaxy install --role-file=requirements.yml --force --roles-path=./roles
                    deactivate
                   '''
                withCredentials([
                        usernamePassword(credentialsId: 'terraform-vsphere', usernameVariable: 'TF_VAR_vsphere_user', passwordVariable: 'TF_VAR_vsphere_password'),
                        usernamePassword(credentialsId: 'slcartifactory', usernameVariable: 'ARTIFACTORY_USERNAME', passwordVariable: 'ARTIFACTORY_PASSWORD'),
                        usernamePassword(credentialsId: 'jenkins-master-ptacontroller', passwordVariable: 'JENKINS_MASTER_PASSWORD', usernameVariable: 'JENKINS_MASTER_USERNAME'),
                        usernamePassword(credentialsId: 'jenkins-nodes-ssh', passwordVariable: 'JENKINS_NODE_PASSWORD', usernameVariable: 'JENKINS_NODE_PASSWORD')]) {
                    sh '''
                        source virt_ansible/bin/activate
                        ansible-playbook -i inventory.py main.yml
                        deactivate
                       '''
                }
            }
        }
        // TODO: At some point it might be nice to parse the ip address or other things from the terraform output and include it in the email.
        stage('Terraform Output') {
            steps {
                withCredentials([
                        usernamePassword(credentialsId: 'terraform-vsphere', usernameVariable: 'TF_VAR_vsphere_user', passwordVariable: 'TF_VAR_vsphere_password'),
                        usernamePassword(credentialsId: 'slcartifactory', usernameVariable: 'ARTIFACTORY_USERNAME', passwordVariable: 'ARTIFACTORY_PASSWORD')]) {
                    sh 'terraform output'
                }
            }
        }
    }
    post {
        failure {
            emailext body: '''$PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS<br><br>Check the console output at ${BUILD_URL}console to view the results.''', mimeType: 'text/html', recipientProviders: [requestor()], subject: '$PROJECT_NAME - Build # $BUILD_NUMBER - $BUILD_STATUS!', to: "pta.admin@company.com"
        }
    }
}