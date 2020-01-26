import json
import subprocess
import os

config = json.loads(open("configuration.json", "r").read())

STDERR_FILE = open("STDERR_FILE", "w")

original_admin_center = os.environ["TBRICKS_ADMIN_CENTER"]

os.environ["TBRICKS_ADMIN_CENTER"] = config["admin_system"]
LOG_DIRECTORY = "component_logs"

if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)
# read component types from JSON file
component_type_list = [config["component_details"][i]["component_type"] for i in range(len(config["component_details"]))]
component_list = []
generate_alert_for_components = []
generic_error_warn_to_skip = []

# read all generic errors and warnings
for i in range (len(config["generic_error_warning_to_skip"])):
    generic_error_warn_to_skip.append(config["generic_error_warning_to_skip"][i]["error_warning"])
generic_error_warn_to_skip = "|".join(generic_error_warn_to_skip)
print(generic_error_warn_to_skip)


data_to_write = ""
for component_type in component_type_list:
    # read all specific errors and warnings
    for i in range (len(config["component_details"][i]         )):
        specific_error_warn_to_skip.append(config["generic_error_warning_to_skip"][i]["error_warning"])
    specific_error_warn_to_skip = "|".join(specific_error_warn_to_skip)
    print(specific_error_warn_to_skip)


    component_list.extend(subprocess.check_output("tbcomponent get type  | egrep -B1 '"+component_type+"' | egrep -v '"+component_type+"|--' | awk '{print $3}'", shell="True").split("\n"))
    component_list.remove("")
    for component in component_list:
        print("\n"+"-"*70+" Checking component "+component+" "+"-"*70)
        try:
            if(config["component_details"][component_type_list.index(component_type)]["specific_error_warning_to_skip"] != "") or (config["common_error_warning_to_skip"] != ""):
                error_warn_to_skip = config["component_details"][component_type_list.index(component_type)]["specific_error_warning_to_skip"] + "|" +config["common_error_warning_to_skip"]
                data_to_write = subprocess.check_output("tblog "+component+" -n | tbgrep -v '"+error_warn_to_skip+"'", shell="True")
            else:
                data_to_write = subprocess.check_output("tblog "+component+" -n ", shell="True")
            if data_to_write:
                OUTPUT_FILE = open(LOG_DIRECTORY+"/"+component+"_check.log", "a+")
                generate_alert_for_components.append(component)
                OUTPUT_FILE.write(data_to_write)
                OUTPUT_FILE.close()
        except subprocess.CalledProcessError as exc:
            STDERR_FILE.write("\nFor Component: "+component+"\nReturn Code: "+str(exc.returncode)+"\nOutput:"+str(exc.output))
    component_list = []
STDERR_FILE.close()
os.environ["TBRICKS_ADMIN_CENTER"] = original_admin_center

print("\n\nAlerts to be sent for following components:")

os.environ["TBRICKS_ADMIN_CENTER"] = original_admin_center

for component in generate_alert_for_components:
    print(component)