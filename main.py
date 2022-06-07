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
    
    if CONFIG:
        """If login success, then deploy resources."""
        print("***********AZ Login Sucessfull!! \n\n\n\n\t\t Deploying the Infra using Azure ARM templates*************")
    
        # Availability Set
        print("Availability Set Creation....")
        as_deploy=az_arm_deploy(resource_group, template_as, param_as, resource="AS")
        print("verify AS:\n\n",as_deploy,az_get_cmd_op(cmd_as_show))

        # VM's
        print("Deploy Virtual machines....",VM1,VM2)
        print(az_arm_deploy(resource_group,template_vm1,param_vm1))
        print(az_arm_deploy(resource_group, template_vm2, param_vm2))
        
        #load balancers
        print("Deploy Load balancer....",LB_name)
        print(az_arm_deploy(resource_group, template_lb, param_lb, resource="LB"))

        #Auto-scale
        print("Deploy VMSS...",vmssName)
        print(az_get_cmd_op(create_vmss))
        print("Verify the VMSS  :",vmssName)
        inst_info=az_get_cmd_op(get_vmss)
        ip=get_ip(inst_info)
        port_list=get_port_lst(inst_info)
        print(inst_info,"\n\n\n\n",ip,port_list)   
        print("Creating autoscale Profile,rules")
        print(az_get_cmd_op(profile1))
        print(az_get_cmd_op(rule1))
        print(az_get_cmd_op(rule2))

        #Monitor:
        print("Create the metric alert")
        az_create_metric_alert(resource_group, VM2, alert1)
        az_get_metric_alert(resource_group, alert1)
        az_create_metric_alert(resource_group, VM1, alert2)
        az_get_metric_alert(resource_group, alert2)
        
        #Create the Dashboard
        print(az_arm_deploy(resource_group,template_db,template_dbparam,resource="DB"))
        if verfiy_status(db_nap,db_name):
            print("Dashboard has been created sucessfully....")
    if TEST:
        #Testing
        print("Test the nginx functionality with high traffic , load balancer test,auto-scale test, dashboard ")
        lb_ip=az_get_cmd_op(get_lb_pubIP)
        print("Load balancer public ip:",lb_ip)
        print("Access the VM through Loadbalancer")
        if vfy_nginx(lb_ip,chk_def):
            print("************Able to access the VM through Load balancer Sucessfully!!!*******************")
        else:
            print("************ ERROR: Unable to access the VM through Load balancer*******************")
        print("Install web application - Arcadia in VM2")
        host_info=az_get_vm_info(VM2)
        host = get_ip(host_info)
        ssh_id=ssh_connect(host[0],port,username,vm_password)
        with SCPClient(ssh_id.get_transport()) as scp:  scp.put('nginx_conf_nap.conf','nginx.conf')
        print(exec_shell_cmd(ssh_id,command_lst,log_file))
        time.sleep(10)
        print(exec_shell_cmd(ssh_id,command_lst2,log_file))
        print("Verify the Dynamic page with nginx app protect")
        if vfy_nginx(host[0],chk_str):
            print("************* Nginx App Protect dynamic page verification with Arcadia Application is Passed!!! **************")
            print("Nap-functionality test with invalid attacks")
            print("======================      cross script      ========================")
            output = attackslib.cross_script_attack(host[0])
            print(output)
            assert "support ID" in output
            print("===================      cross script attack blocked. ================")
            print("======================      sql injection       ========================")
            output = attackslib.sql_injection_attack(host[0])
            print(output)
            assert "support ID" in output
            print("==================   sql injection script attack blocked.  ==================")
            print("======================      command injection       ========================")
            output = attackslib.command_injection_attack(host[0])
            print(output)
            assert "support ID" in output
            print("================      command injection attack blocked. =================")
            print("======================      directory traversal      ========================")
            output = attackslib.directory_traversal_attack(host[0])
            print(output)
            assert "support ID" in output
            print("=================    directory traversal attack blocked.    ===============")
            print("======================      file inclusion      ========================")
            output = attackslib.file_inclusion_attack(host[0])
            print(output)
            assert "support ID" in output
            print("=======================   file inclusion attack blocked.   ======================")
        else:
            print("************* ERROR: Nginx App Protect dynamic page verification is Failed!!! **************")
        ssh_id.close()

        #Load balancer Test
        print("Load balancer TEST with fault tolarance")
        if vfy_nginx(lb_ip,chk_def):
            print("************Load balancer test with default config is passed!!!***************")
        else:
            print("************ ERROR: Load balancer test with default config is Failed!!!***************")
        print("\t\t\t\t************Fault Tolarance TEST !!!!******************")
        az_get_cmd_op(stop_vm1)
        if  vfy_nginx(lb_ip,chk_str):
            print("********** Load balancer test passed in fault tolarance Test!!! ***********")
        else:
            print("********** ERROR: Load balancer test Failed in fault tolarance Test!!! ***********")
        az_get_cmd_op(start_vm1)

        #Auto-scale Test
        print("\t************AutoScale TEST !!!!******************")
        inst_info=az_get_cmd_op(get_vmss)
        ip=get_ip(inst_info)
        port_list=get_port_lst(inst_info)
        #print("Current number of Instances:",port_list)
        print("Login to the instances and impose HIGH TRAFFIC using stress module")
        for port in port_list:
            print("Connecting to ",ip[0],":",port)
            ssh_id=ssh_connect(ip[0],port,username,vm_password)
            ssh_id_lst.append(ssh_id)
            print(exec_shell_cmd(ssh_id,vmss_cmd_lst,log_file,tout=10))
        for ssh_id in ssh_id_lst:
            ssh_id.close()
        print("Wait for 420 seconds [7 minutes] and verify that autoscaling has takes places")
        time.sleep(500)
        inst_info= az_get_cmd_op(get_vmss)   
        print("Number of Instances after imposing high traffic\n\n\n\n",inst_info) 
        if len(get_port_lst(inst_info)) >= 2:
            print("AutoScale functionality is tested for nginx image")
        else:
            print("Error: AutoScale functionality is failed!!!")
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
