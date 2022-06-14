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
print(az_id)

if az_id:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: Module %(module)s :: Line No %(lineno)s :: %(message)s')
    if CONFIG:
        """If login success, then deploy resources."""
        logging.info("AZ Login Sucessfull!!")
        deploy=az_arm_deploy(resource_group,autoscale_template,autoscale_param)
        rule1=az_get_cmd_op(http_rule)
        rule2=az_get_cmd_op(ssh_rule)                      
        logging.info(str(deploy))              
        logging.info(str(rule1))
        logging.info(str(rule2))
        
    if TEST:
        #Get the instance details from Virtual machine scaleset
        inst_info=az_get_cmd_op(get_vmss)
        vmss_ip_lst=get_ip(inst_info)
        vmss_port_list=get_port_lst(inst_info)  
        '''
        instance_state(1,"stop",vmssName,resource_group)
        #logging.info(str(vmss_ip_lst),str(vmss_port_list))
        #logging.info(vmss_ip_lst,vmss_port_list)
        
        #NAP Functional Test
        logging.info("NGINX Functionality Test with Static Page, Dynamic Page, mallicious attacks")
        if vfy_nginx(vmss_ip_lst[0],chk_def):
            logging.info("NGINX Static Page Verification is Completed")
        else:
            logging.info("ERROR:  NGINX Static Page Verification is Failed!!!")
        ssh_id=ssh_connect(vmss_ip_lst[0],vmss_port_list[0],username,vm_password)
        with SCPClient(ssh_id.get_transport()) as scp:  scp.put('nginx_conf_nap.conf','nginx.conf')
        exec_shell_cmd(ssh_id,command_lst,log_file)
        time.sleep(10)
        exec_shell_cmd(ssh_id,command_lst2,log_file)
        try:
            if vfy_nginx(vmss_ip_lst[0],chk_str):
                logging.info("Nginx App Protect dynamic page verification with Arcadia Application is Sucessfull!!!")
                logging.info("NAP  Functionality Test with Invalid Attacks")
                logging.info("======================      cross script      ========================")
                output = attackslib.cross_script_attack(vmss_ip_lst[0])
                logging.info(str(output))
                assert "support ID" in output
                logging.info("===================      cross script attack blocked. ================")
                logging.info("======================      sql injection       ========================")
                output = attackslib.sql_injection_attack(vmss_ip_lst[0])
                logging.info(str(output))
                assert "support ID" in output
                logging.info("==================   sql injection script attack blocked.  ==================")
                logging.info("======================      command injection       ========================")
                output = attackslib.command_injection_attack(vmss_ip_lst[0])
                logging.info(str(output))
                assert "support ID" in output
                logging.info("================      command injection attack blocked. =================")
                logging.info("======================      directory traversal      ========================")
                output = attackslib.directory_traversal_attack(vmss_ip_lst[0])
                logging.info(str(output))
                assert "support ID" in output
                logging.info("=================    directory traversal attack blocked.    ===============")
                logging.info("======================      file inclusion      ========================")
                output = attackslib.file_inclusion_attack(vmss_ip_lst[0])
                logging.info(str(output))
                assert "support ID" in output
                logging.info("=======================   file inclusion attack blocked.   ======================")
            else:
                logging.info("ERROR: Nginx App Protect dynamic page verification is Failed!!! ")
        except BaseException:
            logging.exception("An exception was thrown!")
        ssh_id.close()   
        

        #Load balancer Test
        instance_state(1,"restart",vmssName,resource_group)
        logging.info("Load Balancer TEST with Fault Tolarance")
        instance_state(0,"stop",vmssName,resource_group)
        time.sleep(10)
        
        if vfy_nginx(vmss_ip_lst[0],chk_def):
            logging.info("Load Balancer TEST with Fault Tolarance is Sucessfull")
        else:
            logging.info("Load Balancer TEST with Fault Tolarance is Failed!!!")
        instance_state(0,"restart",vmssName,resource_group)
        vmss_port_list.reverse()
        '''
        #Auto-scale Test
        logging.info("Nginx App Protect WAF - AutoScale TEST ")
        logging.info("Imposing HIGH TRAFFIC using stress module")
        for port in vmss_port_list:
            print("Connecting to ",vmss_ip_lst[0],":",port)
            ssh_id=ssh_connect(vmss_ip_lst[0],port,username,vm_password)
            ssh_id_lst.append(ssh_id)
            exec_shell_cmd(ssh_id,apply_stress,log_file)
        
        logging.info("Minimum of 5min duration is required to trigger the scaling action - WaitTime: 7Minutes")
        time.sleep(400)
        inst_info= az_get_cmd_op(get_vmss)   
        vmss_ip_lst=get_ip(inst_info)
        print("Number of Instances after Imposing high traffic",vmss_ip_lst) 
        if len(get_port_lst(inst_info)) > 2:
            logging.info("Scaling Test is Completed Sucessfully")
        else:
            logging.info("Error: Scaling Test is Failed!!!")
        for sshId in ssh_id_lst:
            exec_shell_cmd(sshId,remove_stress,log_file)
            sshId.close()
        
    if DECONFIG:
        #De-config    
        #time.sleep(60)     
        print("Destroying the Infra.")  
        for alert in [alert1,alert2]:
            az_delete_metric_alert(resource_group,alert)
        for vm in [VM1,VM2]:
            print(az_arm_destroy(resource_group,vm))
        az_lb_destroy(resource_group,LB_name)
        az_as_destroy(resource_group,AS_name)    
        for service in del_cfg:
            az_get_cmd_op(service)
    
else:
    print("Error: Unable to connect to Azure CLI")
