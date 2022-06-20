import time, os, sys, json, ast
path= "/home/runner/work/azure-waf-solution-template-/azure-waf-solution-template-"
sys.path.insert(0, path)
from Lib.utils import *
from Lib.var import *
from Lib.attackslib import *
from art import *


#Get the service principal and secret values
principal= sys.argv[1]
password = sys.argv[2]

print("Connecting to Azure CLI")
az_id = az_login(principal,password,tenantid)
if az_id:          
        print(banner("Validating the user given params"))
        #Get the instance details from Virtual machine scaleset
        inst_info=az_get_cmd_op(get_vmss)
        vmss_ip_lst=get_ip(inst_info)
        vmss_port_list=get_port_lst(inst_info)  
        print("VMSS Instance Details:", vmss_ip_lst, vmss_port_list)       
        
        if NAP_TEST:
            try:
                print(text2art("NAP Functional Testing",font="small"))
                turn_instance_state(str(vmss_port_list[1])[-1],"stop",vmssName,resource_group)
                #NAP Functional Test
                #print("NGINX Functionality Test with Static Page, Dynamic Page, mallicious attacks")
                print(banner("NAP Static Page Verification"))
                if vfy_nginx(vmss_ip_lst[0],chk_def):
                    print("NGINX Static Page Verification is Completed")
                else:
                    print("ERROR:  NGINX Static Page Verification is Failed!!!")
                
                print(banner("NAP Dynamic Page Verification"))
                ssh_id=ssh_connect(vmss_ip_lst[0],vmss_port_list[0],username,vm_password)
                with SCPClient(ssh_id.get_transport()) as scp:  scp.put('Lib/nginx_conf_nap.conf','nginx.conf')
                for cmd in [command_lst,command_lst2]:
                    exec_shell_cmd(ssh_id,cmd)
                    time.sleep(10)
                
                if vfy_nginx(vmss_ip_lst[0],chk_str):
                    print("Nginx App Protect dynamic page verification with Arcadia Application is Successfull!!!")
                    print(banner("NAP Test with Invalid Attacks "))
                    print("\t======================      cross script      ========================")
                    output = cross_script_attack(vmss_ip_lst[0])
                    print("|\t",output)
                    assert "support ID" in output
                    print("\t===================      cross script attack blocked. ================")
                    print("\t======================      sql injection       ========================")
                    output = sql_injection_attack(vmss_ip_lst[0])
                    print(output)
                    assert "support ID" in output
                    print("\t==================   sql injection script attack blocked.  ==================")
                    print("\t======================      command injection       ========================")
                    output = command_injection_attack(vmss_ip_lst[0])
                    print(output)
                    assert "support ID" in output
                    print("\t================      command injection attack blocked. =================")
                    print("\t======================      directory traversal      ========================")
                    output = directory_traversal_attack(vmss_ip_lst[0])
                    print(output)
                    assert "support ID" in output
                    print("\t=================    directory traversal attack blocked.    ===============")
                    print("\t======================      file inclusion      ========================")
                    output = file_inclusion_attack(vmss_ip_lst[0])
                    print(output)
                    assert "support ID" in output
                    print("\t=======================   file inclusion attack blocked.   ======================")
                else:
                    print(banner("ERROR: Nginx App Protect dynamic page verification is Failed!!!"))
                turn_instance_state(str(vmss_port_list[1])[-1],"start",vmssName,resource_group)
            except AssertionError:
                print("Encountered a Problem")
                raise
                
        if LB_TEST:
            print(text2art("LoadBalancer Test",font="small"))                
            print(banner("Load Balancer TEST with Fault Tolarance"))
            turn_instance_state(str(vmss_port_list[1])[-2],"stop",vmssName,resource_group)
            time.sleep(10)

            if vfy_nginx(vmss_ip_lst[0],chk_def):
                print(banner("Load Balancer TEST with Fault Tolarance is Successfull"))
            else:
                print(banner("Load Balancer TEST with Fault Tolarance is Failed!!!"))
            turn_instance_state(str(vmss_port_list[1])[-2],"start",vmssName,resource_group)
            time.sleep(30)
        
        if AutoScale_TEST:
            try:
                print(text2art("Autoscale",font="small"))
                print("Nginx App Protect WAF - AutoScale TEST ")
                print("Current No of instances under VMSS:",vmssName,vmss_ip_lst,vmss_port_list)
                print("Imposing HIGH TRAFFIC on available instances")
                vmss_port_list.reverse()
                for port in vmss_port_list:
                    print("Connecting to ",vmss_ip_lst[0],":",port)
                    ssh_id=ssh_connect(vmss_ip_lst[0],port,username,vm_password)
                    exec_shell_cmd(ssh_id,apply_stress)

                print("Minimum of amount of duration to trigger the auto-scaling action: 6-7 Minutes")
                time.sleep(500)
                inst_info= az_get_cmd_op(get_vmss)   
                vmss_ip_lst=get_ip(inst_info)
                print("Number of Instances after Imposing high traffic",vmss_ip_lst) 
                if len(get_port_lst(inst_info)) > 2:
                    print("Scaling Test is Completed Successfully")
                else:
                    print("Error: Scaling Test is Failed!!!")
                for port in vmss_port_list:
                    ssh_id=ssh_connect(vmss_ip_lst[0],port,username,vm_password)
                    exec_shell_cmd(ssh_id,remove_stress)
            except SSHException as sshException:
                print(banner("Unable to establish SSH connection: %s" % sshException))
else:
    print("Error: Unable to connect to Azure CLI")
