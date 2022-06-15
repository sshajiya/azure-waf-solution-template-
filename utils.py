import subprocess
import paramiko
from scp import SCPClient
import requests,urllib,re
from bs4 import BeautifulSoup
import json
from var import azure_user_json
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


def az_arm_deploy(resource_group, template_file, param_file, resource="cft"):
    """Deploy resources in Azure using templates."""
    try:
        if resource == "cft":
            # update vm params as per user config
            # change_vm_param_file(param_file, azure_user_json)
            print("Create the Stack!!!") 
        elif resource == "DB":
            #change_lb_param_files(template_file, param_file, azure_user_json)
            print("Dashboard Creation!!!")            

        az_deploy= "az deployment group create --resource-group " + resource_group + " --template-file " + template_file + " --parameters " + param_file + " --output table " 
        deploy = subprocess.run(az_deploy, shell = True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        az_dp_out =  deploy.stdout.decode("utf-8")
        az_dp_err =  deploy.stderr.decode("utf-8")
        print(az_deploy,"\n\n",az_dp_out,"\n\n",az_dp_err)
        return az_dp_out
    except:
        return az_dp_err

def az_get_cmd_op(cmd):
    try:
        deploy = subprocess.run(cmd, shell = True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        print(deploy)
        az_vm_out =  deploy.stdout.decode("utf-8")
        az_vm_err =  deploy.stderr.decode("utf-8")
        return az_vm_out
    except:
        return az_vm_err
        
def ssh_connect(host,port,username,password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_id=ssh.connect(host, port, username, password)
        return ssh_id;
    except BaseException:
        logging.exception("An exception was thrown!")
        return False

def exec_shell_cmd(ssh_id,command_lst):
    try:
        for cmd in command_lst:
            stdin, stdout, stderr = ssh_id.exec_command(cmd)
            lines = stdout.readlines()
            for line in lines: print(line)
        return True
    except BaseException:
        logging.exception("An exception was thrown!")
        return False

def turn_instance_state(inst_num,action,vmssName,resource_grp):
    try:
        vm_action= "az vmss " + str(action) + " --instance-ids " + str(inst_num) + " --name "  + vmssName + " --resource-group " + resource_grp + "  --no-wait"
        get_action = subprocess.run(vm_action, shell = True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        print(get_action)
        return True
    except BaseException:
        logging.exception("An exception was thrown!")
        return False

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
    except BaseException:
        logging.exception("An exception was thrown!")
        return False


def get_ip(info):
    try:
        for line in info.split("\n"):
            ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
            if ip:
                return ip
    except:
        return False    

def get_port_lst(info):
    try:
            port = re.findall(r'[0-9]+(?:\.[0-9]+){3}:([0-9]+)?', info)
            if port:
                return port
    except:
        return False
