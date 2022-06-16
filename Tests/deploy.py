import time, os, sys
from LB.utils import *
from LB.var import *

#Get the service principal and secret values
principal= sys.argv[1]
password = sys.argv[2]

print("Connecting to Azure CLI")
az_id = az_login(principal,password,tenantid)
if az_id:
    try:
        """If login success, then deploy resources."""
        print("AZ Login Sucessfull!!")
        #print(az_arm_deploy(resource_group,autoscale_template,autoscale_param))
        #print(az_get_cmd_op(http_rule))
        #print(az_get_cmd_op(ssh_rule))  
        print(az_arm_deploy(resource_group,template_db,template_dbparam))
        dashboard_info=az_get_cmd_op(db_verify)
        if db_name in dashboard_info:
            print("Dashboard Created Sucessufully")
    except BaseException:
        logging.exception("An exception was thrown!")
else:
    print("Error: Unable to connect to Azure CLI")
