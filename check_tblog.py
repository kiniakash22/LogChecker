#!/usr/bin/python
import xml.dom.minidom
import subprocess
import os
from datetime import datetime

NOW = datetime.now()
doc = xml.dom.minidom.parse("configuration.xml")
STDERR_FILE = open("/opt/tbricks/logs/component_logs/STDERR_FILE_"+NOW.strftime("%Y-%m-%d_%H:%M"), "w")

original_admin_center = os.environ["TBRICKS_ADMIN_CENTER"]
original_path = os.environ["PATH"]
#os.environ["TBRICKS_ADMIN_CENTER"] = config["admin_system"]
LOG_DIRECTORY = "/opt/tbricks/logs/component_logs"

if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)
    
# read component types from XML file
component_type_list = [component.getAttribute("type") for component in doc.getElementsByTagName("component") if component.getAttribute("type")!="ALL"]

generic_error_warn_to_skip = []
generic_error_warn_to_search = []
specific_error_warn_to_skip = []
specific_error_warn_to_search = []
component_name_list = []   # stores short_name for each component type
generate_alert_for_components = []

def get_all_error_warn(domObject):
    #global generic_error_warn_to_skip, generic_error_warn_to_search
    error_warn_to_skip = []
    error_warn_to_search = []
    for error_warn in component_type.getElementsByTagName("error_warn"):  
        # check whether skip is set to true
        if (error_warn.getAttribute("skip") in ("true", "True")):        
            error_warn_to_skip.append(str(error_warn.getAttribute("type")))
        else:
            error_warn_to_search.append(str(error_warn.getAttribute("type")))
    return (error_warn_to_skip, error_warn_to_search)


def append_all_error_warn(generic_error_warn, specific_error_warn):
    if (generic_error_warn == ""):
        term = specific_error_warn
    elif (specific_error_warn == ""):
        term = generic_error_warn
    else:
        term = generic_error_warn+"|"+specific_error_warn
    return term


for admin_system in doc.getElementsByTagName("admin_system"):  
    # set admin system
    current_admin_system = admin_system.getAttribute("name")
    os.environ["TBRICKS_ADMIN_CENTER"] = current_admin_system

    # get and set PATH to tbricks bin/ directory
    old_path = os.environ["PATH"]
    new_path = admin_system.getAttribute("path")+":"+old_path
    
    print("\n\n"+"-*"*35+" Checking Admin System: "+current_admin_system+" "+"*-"*35)
    # loop through all <component> tags
    for component_type in doc.getElementsByTagName("component"):  
        # check if component type is ALL to get generic error/warning                        
        if (component_type.getAttribute("type") == "ALL"):  
            skip, search = get_all_error_warn(component_type)
            generic_error_warn_to_skip = "|".join(skip)
            generic_error_warn_to_search = "|".join(search)
        else:
            skip, search = get_all_error_warn(component_type)
            specific_error_warn_to_skip = "|".join(skip)
            specific_error_warn_to_search = "|".join(search)

            component_name_list.extend(subprocess.check_output(admin_system.getAttribute("path")+"tbcomponent get type  | egrep -B1 '"+component_type.getAttribute("type")+"' | egrep -v '"+component_type.getAttribute("type")+"|--' | awk '{print $3}'", shell="True").split("\n"))
            component_name_list.remove("")

            # loop through all individual components of type <component>
            for component in component_name_list:
                # append all skip terms
                skip = append_all_error_warn(generic_error_warn_to_skip, specific_error_warn_to_skip)
                # append all skip terms
                search = append_all_error_warn(generic_error_warn_to_search, specific_error_warn_to_search)

                print("\n"+"-"*70+" Checking component "+component+" "+"-"*70)
                try:
                    if(skip != ""):
                        #error_warn_to_skip = config["component_details"][component_type_list.index(component_type)]["specific_error_warning_to_skip"] + "|" +config["common_error_warning_to_skip"]
                        data_to_write = subprocess.check_output(admin_system.getAttribute("path")+"tblog "+component+" -n | tbgrep -v '"+skip+"'", shell="True")
                    else:
                        data_to_write = subprocess.check_output(admin_system.getAttribute("path")+"tblog "+component+" -n ", shell="True")
                    if data_to_write:
                        file_name = LOG_DIRECTORY+"/check_"+component+"_"+NOW.strftime("%Y-%m-%d_%H:%M")+".log"
                        OUTPUT_FILE = open(file_name, "w+")
                        generate_alert_for_components.append(component)
                        OUTPUT_FILE.write(data_to_write)
                        OUTPUT_FILE.close()
                except subprocess.CalledProcessError as exc:
                    STDERR_FILE.write("\nFor Component: "+component+" of Admin System:"+current_admin_system+"\nReturn Code: "+str(exc.returncode)+"\nOutput:"+str(exc.output))
                component_name_list = []
                skip = ""
                search = ""

STDERR_FILE.close()

# reset original admin system and path
os.environ["TBRICKS_ADMIN_CENTER"] = original_admin_center
os.environ["PATH"] = original_path

print("\n\nAll logs saved in directory: /opt/tbricks/logs/component_logs/")
print("\nSTD ERR copied to file: /opt/tbricks/logs/component_logs/STDERR_FILE")
print("\nAlerts to be sent for following components:")

os.environ["TBRICKS_ADMIN_CENTER"] = original_admin_center

for component in generate_alert_for_components:
    print(component)