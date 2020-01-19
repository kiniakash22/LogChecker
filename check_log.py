import sys
import json
import os
import subprocess

config = json.loads(open("configuration.json", "r").read())

STDERR_FILE = open("STDERR_FILE", "w")
OUTPUT_FILE = open("OUTPUT_FILE", "w")

# read component types from JSON file
component_type_list = [config["component_details"][i]["component_type"] for i in range(len(config["component_details"]))]
component_list = []
component_list_checked = []
temp = ""
for component_type in component_type_list:
    component_list.extend(subprocess.check_output("tbcomponent get type  | grep -B1 '"+component_type+"' | egrep -v '"+component_type+"|--' | awk '{print $3}'", shell="True").split("\n"))
    component_list.remove("")
    for component in component_list:
        #component = "sdn_eutlx_gtp_md"
        try:
            if(config["component_details"][i]["error_warn_to_skip"] != ""):
                OUTPUT_FILE.write(subprocess.check_output("tblog "+component+" -k date 30M -n | grep -v '"+config["component_details"][i]["error_warn_to_skip"]+"'", shell="True"))
            else:
                OUTPUT_FILE.write(subprocess.check_output("tblog "+component+" -k date 30M -n ", shell="True"))

        except subprocess.CalledProcessError as exc:
            STDERR_FILE.write("\nFor Component: "+component+"\nReturn Code: "+str(exc.returncode)+"\nOutput:"+str(exc.output))

        print(component)
    component_list_checked.extend(component_list)
    component_list = []

print(component_list_checked)