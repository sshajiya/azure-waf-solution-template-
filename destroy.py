import time, os, sys
from utils import *
from var import *
import attackslib

#Get the service principal and secret values
principal= sys.argv[1]
password = sys.argv[2]

print("Connecting to Azure CLI")
az_id = az_login(principal,password,tenantid)
if az_id:
    try:            
        print("Destroying the Infra.")  
        for service in del_cfg:
            az_get_cmd_op(service) 
    except BaseException:
        logging.exception("An exception was thrown under Destroy!")
else:
    print("Error: Unable to connect to Azure CLI")
