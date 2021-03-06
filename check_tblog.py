#!/bin/python
import xml.dom.minidom
import subprocess
import os
import sys
from datetime import datetime
  
NOW = datetime.now()
SCRIPT_PATH = "/opt/tbricks/scripts/check_tblog/"
doc = xml.dom.minidom.parse(SCRIPT_PATH+"configuration.xml")

# set default log time to 61 Minutes if nothing is specified
tblog_time = "61M"

if (len(sys.argv) > 2) or (len(sys.argv) == 2 and (sys.argv[1][-1] not in ("m", "M"))):
    print("Incorrect Syntax!!!\nUsage: <python> <script_name.py> [time in minutes]\ne.g. python check_tblog.py 45M")
    std_err_file_name = "/opt/tbricks/logs/component_logs/STDERR_FILE_"+NOW.strftime("%Y-%m-%d_%H:%M")
    STDERR_FILE = open(std_err_file_name, "w")
    STDERR_FILE.write("Incorrect Syntax!!!\nUsage: <python> <script_name.py> [time in minutes]\ne.g. python check_tblog.py 45M")
    STDERR_FILE.close()
    sys.exit()
elif len(sys.argv) == 2:
    tblog_time = str(int(sys.argv[1][:-1])+1)+sys.argv[1][-1]

os.environ["TBRICKS_ADMIN_CENTER"] = "temp"

original_path = os.environ["PATH"]
#os.environ["TBRICKS_ADMIN_CENTER"] = config["admin_system"]
LOG_DIRECTORY = "/opt/tbricks/logs/component_logs"

if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

subprocess.call(['chmod', '0777', LOG_DIRECTORY])

# read component types from XML file
component_type_list = [component.getAttribute("type") for component in doc.getElementsByTagName("component") if component.getAttribute("type")!="ALL"]

generic_error_warn_to_skip = []
generic_error_warn_to_search = []
specific_error_warn_to_skip = []
specific_error_warn_to_search = []
component_name_list = []   # stores short_name for each component type
generate_alert_for_components = []
std_err_file_name = ""
command_executed = ""

def get_all_error_warn(domObject):
    #global generic_error_warn_to_skip, generic_error_warn_to_search
    error_warn_to_skip = []
    error_warn_to_search = []
    for error_warn in component_type.getElementsByTagName("error_warn"):  
        # check whether skip is set to true
        if (error_warn.getAttribute("skip") in ("true", "True")):        
            error_warn_to_skip.append(str(error_warn.getAttribute("value")))
        else:
            error_warn_to_search.append(str(error_warn.getAttribute("value")))
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
    
    print("\n\n"+"-*"*20+" Checking Admin System: "+current_admin_system+" "+"*-"*20)
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

            # append all skip terms
            skip = append_all_error_warn(generic_error_warn_to_skip, specific_error_warn_to_skip)
            # append all skip terms
            search = append_all_error_warn(generic_error_warn_to_search, specific_error_warn_to_search)
            print("\n"+"-"*40+" Checking Components of Type: "+component_type.getAttribute("type")+" "+"-"*40)

            # get list of all the components to be skipped
            skip_component_list = doc.getElementsByTagName("skip_list")[0].getAttribute("short_name").replace(" ","").split(",")
            component_name_list = (component for component in component_name_list if component not in (skip_component_list))

            # loop through all individual components of type <component>
            for component in component_name_list:
                print("\n"+"-"*40+" Checking Component: "+component+" "+"-"*40)
                try:
                    if(skip != ""):
                        command_executed = "Command executed:\n"+admin_system.getAttribute("path")+"tblog "+component+" -n -k date "+tblog_time+" | "+admin_system.getAttribute("path")+"tbgrep -v '"+skip+"'\n\n\n"
                        data_to_write = subprocess.check_output(admin_system.getAttribute("path")+"tblog "+component+" -n -k date "+tblog_time+" | "+admin_system.getAttribute("path")+"tbgrep -v '"+skip+"'", shell="True")

                    else:
                        command_executed = "Command executed:\n"+admin_system.getAttribute("path")+"tblog "+component+" -n  -k date "+tblog_time+"\n\n\n" 
                        data_to_write = subprocess.check_output(admin_system.getAttribute("path")+"tblog "+component+" -n  -k date "+tblog_time, shell="True")
                    
                    if data_to_write:
                        file_name = LOG_DIRECTORY+"/check_"+component+"_"+NOW.strftime("%Y-%m-%d_%H:%M")+".log"
                        OUTPUT_FILE = open(file_name, "a+")
                        subprocess.call(['chmod', '0777', file_name])
                        generate_alert_for_components.append(component)
                        OUTPUT_FILE.write(command_executed)
                        OUTPUT_FILE.write(data_to_write)
                        OUTPUT_FILE.close()
                except subprocess.CalledProcessError as exc:
                    std_err_file_name = "/opt/tbricks/logs/component_logs/STDERR_FILE_"+NOW.strftime("%Y-%m-%d_%H:%M")
                    STDERR_FILE = open(std_err_file_name, "a+")
                    STDERR_FILE.write("\nFor Component: "+component+" of Admin System:"+current_admin_system+"\nReturn Code: "+str(exc.returncode)+"\nOutput:"+str(exc.output))
            component_name_list = []
            skip = ""
            search = ""
if os.path.exists(std_err_file_name):
    subprocess.call(['chmod', '0777', std_err_fil_name])
    print("\nSTD ERR copied to file: /opt/tbricks/logs/component_logs/"+std_err_file_name)
    STDERR_FILE.close()

# reset original admin system and path
os.environ["PATH"] = original_path

print("\n\nAll logs saved in directory: /opt/tbricks/logs/component_logs/")
print("\nAlerts to be sent for following components:")


for component in generate_alert_for_components:
    print(component)

# Author: akash.kini@itiviti.com
