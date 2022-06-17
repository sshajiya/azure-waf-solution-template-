import subprocess,os,sys
path= "/home/runner/work/azure-waf-solution-template-/azure-waf-solution-template-"
sys.path.insert(0, path)
from Lib.var import azure_user_json
import paramiko
from scp import SCPClient
import requests,urllib,re
from bs4 import BeautifulSoup
import json
import logging


#Methods
def az_login(principal,password,tenantid):
    try:  
        chk= subprocess.run("az version", shell = True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        sp_create = "az login --service-principal -u " + principal + " -p " + password + " --tenant " + tenantid
        az_cli_login = subprocess.run(sp_create, shell = True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        return az_cli_login
    except BaseException:
        logging.exception("An exception was thrown!")
        return False

def update_param_file(param_file,resource="cft"):
    
    """Change vm deploy params dynamically as per user configuration."""
    param_file_handler = open(param_file, 'r')
    param_file_data = json.load(param_file_handler)
    param_file_handler.close()

    # fetch user details from json
    azure_user_handler = open(azure_user_json,"r")
    azure_user_data = json.load(azure_user_handler)    
    azure_user_handler.close()
    
    if resource == "cft":
        
        # update params in cft deploy template
        param_file_data["parameters"]["location"]["value"] = azure_user_data["location_name"]
        param_file_data["parameters"]["virtualNetworkId"]["value"] = "/subscriptions/"+azure_user_data["subscriptionId"]+"/resourceGroups/"+azure_user_data["resourceGroup"]+"/providers/Microsoft.Network/virtualNetworks/"+azure_user_data["virnetworkId"]
        param_file_data["parameters"]["virtualNetworkName"]["value"] = azure_user_data["virnetworkId"]
        param_file_data["parameters"]["networkSecurityGroups"]["value"][0]["name"]= "basicNsg"+azure_user_data["virnetworkId"]+"-nic01"
        param_file_data["parameters"]["networkSecurityGroups"]["value"][0]["id"] = "/subscriptions/"+azure_user_data["subscriptionId"]+"/resourceGroups/"+azure_user_data["resourceGroup"]+"/providers/Microsoft.Network/networkSecurityGroups/"+"basicNsg"+azure_user_data["virnetworkId"]+"-nic01"
        param_file_data["parameters"]["networkInterfaceConfigurations"]["value"][0]["name"]= azure_user_data["virnetworkId"]+"-nic01"
        param_file_data["parameters"]["networkInterfaceConfigurations"]["value"][0]["subnetId"]="/subscriptions/"+azure_user_data["subscriptionId"]+"/resourceGroups/"+azure_user_data["resourceGroup"]+"/providers/Microsoft.Network/virtualNetworks/"+azure_user_data["virnetworkId"]+"/subnets/default"
        param_file_data["parameters"]["networkInterfaceConfigurations"]["value"][0]["nsgName"]="basicNsg"+azure_user_data["virnetworkId"]+"-nic01"
        param_file_data["parameters"]["networkInterfaceConfigurations"]["value"][0]["nsgId"] = "/subscriptions/"+azure_user_data["subscriptionId"]+"/resourceGroups/"+azure_user_data["resourceGroup"]+"/providers/Microsoft.Network/networkSecurityGroups/"+"basicNsg"+azure_user_data["virnetworkId"]+"-nic01"
        param_file_data["parameters"]["publicIpAddressName"]["value"] = azure_user_data["cftName"]+"-ip"
        param_file_data["parameters"]["backendPoolName"]["value"] = azure_user_data["cftName"]+"-bepool"
        param_file_data["parameters"]["loadBalancerName"]["value"] = azure_user_data["cftName"]+"-lb"
        param_file_data["parameters"]["inboundNatPoolId"]["value"] = "/subscriptions/"+azure_user_data["subscriptionId"]+"/resourceGroups/"+azure_user_data["resourceGroup"]+"/providers/Microsoft.Network/loadBalancers/"+azure_user_data["cftName"]+"-lb/inboundNatPools/natpool"
        param_file_data["parameters"]["backendPoolId"]["value"] =  "/subscriptions/"+azure_user_data["subscriptionId"]+"/resourceGroups/"+azure_user_data["resourceGroup"]+"/providers/Microsoft.Network/loadBalancers/"+azure_user_data["cftName"]+"-lb/backendAddressPools/"+azure_user_data["cftName"]+"-bepool"
        param_file_data["parameters"]["vmName"]["value"]=azure_user_data["cftName"]
        param_file_data["parameters"]["virtualMachineScaleSetName"]["value"]=azure_user_data["cftName"]
        param_file_data["parameters"]["adminUsername"]["value"]=azure_user_data["adminUsername"]
        param_file_data["parameters"]["adminPassword"]["value"]=azure_user_data["adminPassword"]
        param_file_data["parameters"]["autoscaleDiagnosticLogsWorkspaceId"]["value"]="/subscriptions/"+azure_user_data["subscriptionId"]+"/resourceGroups/"+azure_user_data["resourceGroup"]+"/providers/Microsoft.operationalinsights/workspaces/"+azure_user_data["workspaceName"]
    
    elif resource == "cft":
        # update params in Dashboard template
        param_file_data["parameters"]["dashboards_name"]["value"] = azure_user_data["dashboard_name"]
        param_file_data["parameters"]["location"]["value"] = azure_user_data["location_name"]
        param_file_data["parameters"]["loadBalancerName"]["value"] = "/subscriptions/"+azure_user_data["subscriptionId"]+"/resourceGroups/"+azure_user_data["resourceGroup"]+"/providers/Microsoft.Network/loadBalancers/"+azure_user_data["cftName"]+"-lb"
        param_file_data["parameters"]["vmssName"]["value"] = "/subscriptions/"+azure_user_data["subscriptionId"]+"/resourceGroups/"+azure_user_data["resourceGroup"]+"/providers/Microsoft.Compute/virtualMachineScaleSets/"+azure_user_data["cftName"]
        
        
    #Re-wrire the template
    jsonFile = open(param_file, "w+")
    jsonFile.write(json.dumps(param_file_data))
    jsonFile.close()

#This function is generated to deploy the ARM template
def az_arm_deploy(resource_group, template_file, param_file, resource="cft"):
    """Deploy resources in Azure using templates."""
    try:
        # update vm params as per user config
        update_param_file(param_file,resource)
        az_deploy= "az deployment group create --resource-group " + resource_group + " --template-file " + template_file + " --parameters " + param_file + " --output table " 
        deploy = subprocess.run(az_deploy, shell = True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        az_dp_out =  deploy.stdout.decode("utf-8")
        az_dp_err =  deploy.stderr.decode("utf-8")
        print(az_dp_out,"\n\n",az_dp_err)
        return az_dp_out
    except:
        return az_dp_err

#This function will execute az cli commmand and returns the output
def az_get_cmd_op(cmd):
    try:
        output = subprocess.run(cmd, shell = True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        az_cmd_out =  output.stdout.decode("utf-8")
        az_cmd_err =  output.stderr.decode("utf-8")
        print(az_cmd_out,"\n\n",az_cmd_err)
        return az_cmd_out
    except:
        return False

#This function will connect to instances through SSH        
def ssh_connect(host,port,username,password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
        return ssh;
    except SSHException as sshException:
        print("Unable to establish SSH connection: %s" % sshException)
        return False

#This function executes commands under ssh console
def exec_shell_cmd(ssh_id,command_lst):
    try:
        for cmd in command_lst:
            stdin, stdout, stderr = ssh_id.exec_command(cmd)
            lines = stdout.readlines()
            for line in lines: print(line)
        return True
    except SSHException as sshException:
        print("Unable to establish SSH connection: %s" % sshException)
        return False

#This function turns off/on/restart the vm instances
def turn_instance_state(inst_num,action,vmssName,resource_grp):
    try:
        vm_action= "az vmss " + str(action) + " --instance-ids " + str(inst_num) + " --name "  + vmssName + " --resource-group " + resource_grp + "  --no-wait"
        get_action = subprocess.run(vm_action, shell = True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        print(get_action)
        return True
    except BaseException:
        logging.exception("An exception was thrown!")
        return False

#This function verify the http status of LB
def vfy_nginx(url,cond_chk):
    try:
        if "http" not in url:
            url="http://"+url
        data = urllib.request.urlopen(url).read()
        bsoup = BeautifulSoup(data, "html.parser")
        title = bsoup.find('title')
        print(title)
        if cond_chk in title.string:
            return True
        else:
            return False
    except urllib.error.HTTPError as e:
        print(e.__dict__)
        return False
    except urllib.error.URLError as e:
        print(e.__dict__)
        return False

#This function returns the IP address lst from a given content
def get_ip(info):
    try:
        for line in info.split("\n"):
            ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
            if ip:
                return ip
    except:
        return False    

#This function returns the Port lst from a given content
def get_port_lst(info):
    try:
            port = re.findall(r'[0-9]+(?:\.[0-9]+){3}:([0-9]+)?', info)
            if port:
                return port
    except:
        return False
