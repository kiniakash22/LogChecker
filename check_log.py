import sys
import json
import os
import subprocess

config = json.loads(open("configuration.json", "r").read())

# read component types from JSON file
component_type_list = [config["component_details"][i]["component_type"] for i in range(len(config["component_details"]))]
component_list = []
for component_type in component_type_list:
    component_list.append(subprocess.check_output("tbcomponent get type | grep -B1 component_type | egrep -v '\"'+component_type+'|--\"' | awk '{print $3}'"))
    component_list.append(subprocess.Popen(["tbcomponent", "ls"]))
    
print(component_list)