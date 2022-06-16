import time, os, sys
from utils import *
from var import *
import attackslib
import json


#Get the service principal and secret values
principal= sys.argv[1]
password = sys.argv[2]

print("Connecting to Azure CLI")
az_id = az_login(principal,password,tenantid)

if az_id:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: Module %(module)s :: Line No %(lineno)s :: %(message)s')
    if CONFIG:
        """If login success, then deploy resources."""
        print("AZ Login Sucessfull!!")
        print(az_arm_deploy(resource_group,autoscale_template,autoscale_param))
        print(az_arm_deploy(resource_group,template_db,template_dbparam))
        print(az_get_cmd_op(http_rule))
        print(az_get_cmd_op(ssh_rule))                 
        
    if TEST:
        #Get the instance details from Virtual machine scaleset
        inst_info=az_get_cmd_op(get_vmss)
        vmss_ip_lst=get_ip(inst_info)
        vmss_port_list=get_port_lst(inst_info)  
        print("VMSS Instance Details:", vmss_ip_lst, vmss_port_list)
        instance_state(1,"stop",vmssName,resource_group)
        
        #NAP Functional Test
        print("NGINX Functionality Test with Static Page, Dynamic Page, mallicious attacks")
        if vfy_nginx(vmss_ip_lst[0],chk_def):
            print("NGINX Static Page Verification is Completed")
        else:
            print("ERROR:  NGINX Static Page Verification is Failed!!!")
        ssh_id=ssh_connect(vmss_ip_lst[0],vmss_port_list[0],username,vm_password)
        with SCPClient(ssh_id.get_transport()) as scp:  scp.put('nginx_conf_nap.conf','nginx.conf')
        exec_shell_cmd(ssh_id,command_lst,log_file)
        time.sleep(10)
        exec_shell_cmd(ssh_id,command_lst2,log_file)
        ssh_id.close() 
        try:
            if vfy_nginx(vmss_ip_lst[0],chk_str):
                print("Nginx App Protect dynamic page verification with Arcadia Application is Sucessfull!!!")
                print("NAP  Functionality Test with Invalid Attacks")
                print("======================      cross script      ========================")
                output = attackslib.cross_script_attack(vmss_ip_lst[0])
                print(output)
                assert "support ID" in output
                print("===================      cross script attack blocked. ================")
                print("======================      sql injection       ========================")
                output = attackslib.sql_injection_attack(vmss_ip_lst[0])
                print(output)
                assert "support ID" in output
                print("==================   sql injection script attack blocked.  ==================")
                print("======================      command injection       ========================")
                output = attackslib.command_injection_attack(vmss_ip_lst[0])
                print(output)
                assert "support ID" in output
                print("================      command injection attack blocked. =================")
                print("======================      directory traversal      ========================")
                output = attackslib.directory_traversal_attack(vmss_ip_lst[0])
                print(output)
                assert "support ID" in output
                print("=================    directory traversal attack blocked.    ===============")
                print("======================      file inclusion      ========================")
                output = attackslib.file_inclusion_attack(vmss_ip_lst[0])
                print(output)
                assert "support ID" in output
                print("=======================   file inclusion attack blocked.   ======================")
            else:
                print("ERROR: Nginx App Protect dynamic page verification is Failed!!! ")
        except BaseException:
            logging.exception("An exception was thrown!")
          
        #Load balancer Test
        instance_state(1,"restart",vmssName,resource_group)
        print("Load Balancer TEST with Fault Tolarance")
        instance_state(0,"stop",vmssName,resource_group)
        time.sleep(10)
        
        if vfy_nginx(vmss_ip_lst[0],chk_def):
            print("Load Balancer TEST with Fault Tolarance is Sucessfull")
        else:
            print("Load Balancer TEST with Fault Tolarance is Failed!!!")
        instance_state(0,"restart",vmssName,resource_group)
        vmss_port_list.reverse()
        
        #Auto-scale Test
        print("Nginx App Protect WAF - AutoScale TEST ")
        print("Current No of instances under VMSS:",vmssName,vmss_ip_lst)
        print("Imposing HIGH TRAFFIC on available instances")
        for port in vmss_port_list:
            print("Connecting to ",vmss_ip_lst[0],":",port)
            ssh_id=ssh_connect(vmss_ip_lst[0],port,username,vm_password)
            ssh_id_lst.append(ssh_id)
            exec_shell_cmd(ssh_id,apply_stress,log_file)
        
        print("Minimum of amount of duration to trigger the auto-scaling action: 6-7 Minutes")
        time.sleep(500)
        inst_info= az_get_cmd_op(get_vmss)   
        vmss_ip_lst=get_ip(inst_info)
        print("Number of Instances after Imposing high traffic",vmss_ip_lst) 
        if len(get_port_lst(inst_info)) > 2:
            print("Scaling Test is Completed Sucessfully")
        else:
            print("Error: Scaling Test is Failed!!!")
        for sshId in ssh_id_lst:
            exec_shell_cmd(sshId,remove_stress,log_file)
            sshId.close()       
        
    if DECONFIG:
        #De-config         
        print("Destroying the Infra.")  
        for service in del_cfg:
            az_get_cmd_op(service)    
else:
    print("Error: Unable to connect to Azure CLI")
