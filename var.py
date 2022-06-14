import json

azure_user_handler = open("azure_user_params.json", "r")
azure_user_data = json.load(azure_user_handler)
tenantid = azure_user_data["CLOUD_CONSOLE_TENANTID"]
resource_group = azure_user_data["CLOUD_CONSOLE_RG"]
username = azure_user_data["adminUsername"]
vm_password = azure_user_data["adminPassword"]

#flag declaration
CONFIG=False
TEST=True
DECONFIG=False

#Variable Declaration
vm_name= "Nginx" 
log_file= "vm_log.txt"
port = 22
#command_lst = ["sudo mv nginx.conf /etc/nginx/nginx.conf" ,"sudo ls /etc/nginx", "sudo cp nginx.conf /etc/nginx/nginx.conf", "cat /etc/nginx/nginx.conf", "sudo systemctl restart nginx"]
command_lst = ["ls", "sudo mv nginx.conf /etc/nginx/nginx.conf" , "sudo systemctl restart nginx"]
command_lst2 = ["systemctl status nginx","systemctl status nginx-app-protect.service","cat /etc/nginx/nginx.conf"]
vmss_cmd_lst=["sudo apt-get update","sudo apt-get -y install stress","sudo stress --cpu 10 --timeout 420 &", "chr(3)"]
apply_stress= ["for i in $(seq $(getconf _NPROCESSORS_ONLN)); do yes > /dev/null & done"]
remove_stress=["killall yes"]
chk_str="Arcadia Finance"
chk_def = "Welcome to NGINX Plus on Azure"
template_as="as_deploy.json"
param_as="as_deploy_params.json"
template_vm1="vm1_deploy.json"
param_vm1="vm1_deploy_params.json"
template_vm2="vm2_deploy.json"
param_vm2="vm2_deploy_params.json"
template_lb="lb_deploy.json"
param_lb="lb_deploy_params.json"
autoscale_template= "nap-autoscale-ubuntu-dev.json"
autoscale_param= "nap-autoscale-ubuntu-dev-params.json"
AS_name="DemoAS"
VM1= "demoVM1"
VM2= "demoVM2"
alert1= "cpu_alert"
alert2= "cpu_alert2"
LB_name= "DemoLB"
ssh_id_lst=[]
azure_user_json= "azure_user_params.json"
template_db="dashboard.json"
template_dbparam="dashboard-params.json"
#########
vnet_name= "user-shshaik-vnet2"
vmssName= "azure-cft"
vmss_lb= "azure-cft-lb"
get_lb_pubIP="az network public-ip show --resource-group " + resource_group + " --name " + vmss_lb + " --query [ipAddress] --output tsv"
sg_name= "basicNsg" + vnet_name + "-nic01"
http_rule= "az network nsg rule create -g " + resource_group + " --nsg-name " + sg_name + " --name httpRule --direction inbound --destination-port-range 80 --access allow --priority 102"
ssh_rule=  "az network nsg rule create -g " + resource_group + " --nsg-name " + sg_name + " --name sshRule --direction inbound --destination-port-range 22 --access allow --priority 101"
restart_vm= "az vmss restart --instance-ids 0 --name azure-cft --resource-group " + resource_group + "  --no-wait"
stop_vm1= "az vm stop -g " + resource_group + " -n " + VM1
start_vm1= "az vm start -g " + resource_group + " -n " + VM1
cmd_as_show="az vm availability-set show --name  " + AS_name + " --resource-group " + resource_group 
cmd_vm1_show= "az vm get-instance-view --name " + VM1 + " --resource-group " + resource_group
cmd_vm2_show= "az vm get-instance-view --name " + VM2 + " --resource-group " + resource_group
cmd_lb_show= "az network lb frontend-ip list -g " + resource_group + " --lb-name " + LB_name


db_name= "Dashboard-NAP-Test"
db_nap="az portal dashboard show --name " + db_name + " --resource-group " + resource_group

autoscale_profile= vmssName +"_profile"
create_vmss = "az vmss create   --resource-group " + resource_group  + " --name " +  vmssName + " --image UbuntuLTS   --upgrade-policy-mode automatic   --instance-count 2   --admin-username " + username  + " --admin-password " + vm_password
get_vmss= "az vmss list-instance-connection-info   --resource-group " + resource_group + " --name " + vmssName + " --output table"
profile1= "az monitor autoscale create   --resource-group " + resource_group + " --resource " + vmssName + " --resource-type Microsoft.Compute/virtualMachineScaleSets   --name " + autoscale_profile + "  --min-count 2   --max-count 10   --count 2 "
rule1= "az monitor autoscale rule create   --resource-group " + resource_group + " --autoscale-name " + autoscale_profile + '  --condition "Percentage CPU > 70 avg 5m"   --scale out 1 '
rule2= "az monitor autoscale rule create   --resource-group " + resource_group + " --autoscale-name " + autoscale_profile + '  --condition "Percentage CPU < 30 avg 5m"   --scale in 1 '
del_vmss= "az vmss delete  --name " + vmssName + " --resource-group " + resource_group
del_vmss_lb= "az network lb delete --name " + vmssName + vmss_lb + "  --resource-group " + resource_group
del_dashboard="az portal dashboard delete --name " + db_name + "  --resource-group " + resource_group + " -y "
del_vmss_ip= " az network public-ip delete -g " + resource_group + " -n " + "azure-cft-ip"
del_vmss_lb_ip=" az network public-ip delete -g " + resource_group + " -n " + "autoscale-DemoLBPublicIP"
del_pub_ip="az network public-ip delete -g " + resource_group + " -n " + "DemoIP"
del_cfg=[del_vmss,del_vmss_lb,del_dashboard,del_vmss_ip,del_vmss_lb_ip,del_pub_ip]
