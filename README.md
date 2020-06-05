# pta-controller-node-01

This host is to be a Jenkins node solely used for running Packer builds,
specifically with the 'vmware-iso' builder because VMware Workstation is installed.

## Jenkins

You shouldn't need to run this by hand. You should be able to run it from the PTAController now.

1. This assumes you have Artifactory configured as the backend. 
If you do not, adjust the main.tf appropriately and be prepared to get that terraform state
backed up into Artifactory once you do have Artifactory up and running.

1. Create the job in PTAController Jenkins to create and configure this VM.

1. Create all of the needed credential objects in PTAController Jenkins.

1. At the bottom of the Jenkinsfile, ensure you change the email address to your PTA 
administrator's address so they get failure notifications.

1. Modify the main.tf to reflect your vsphere's particulars.