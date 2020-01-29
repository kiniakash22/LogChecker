import xml.dom.minidom
import subprocess
import os

doc = xml.dom.minidom.parse("configuration.xml")
STDERR_FILE = open("STDERR_FILE", "w")

original_admin_center = os.environ["TBRICKS_ADMIN_CENTER"]

#os.environ["TBRICKS_ADMIN_CENTER"] = config["admin_system"]
LOG_DIRECTORY = "/opt/tbricks/logs/component_logs"

if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)
    
# read component types from XML file
component_type_list = [component.getAttribute("type") for component in doc.getElementsByTagName("component") if component.getAttribute("type")!="ALL"]

print(component_type_list)

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

        component_name_list.extend(subprocess.check_output("tbcomponent get type  | egrep -B1 '"+component_type.getAttribute("type")+"' | egrep -v '"+component_type.getAttribute("type")+"|--' | awk '{print $3}'", shell="True").split("\n"))
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
                    data_to_write = subprocess.check_output("tblog "+component+" -n | tbgrep -v '"+skip+"'", shell="True")
                else:
                    data_to_write = subprocess.check_output("tblog "+component+" -n ", shell="True")
                if data_to_write:
                    OUTPUT_FILE = open(LOG_DIRECTORY+"/"+component+"_check.log", "w+")
                    generate_alert_for_components.append(component)
                    OUTPUT_FILE.write(data_to_write)
                    OUTPUT_FILE.close()
            except subprocess.CalledProcessError as exc:
                STDERR_FILE.write("\nFor Component: "+component+"\nReturn Code: "+str(exc.returncode)+"\nOutput:"+str(exc.output))
            component_name_list = []
            skip = ""
            search = ""

STDERR_FILE.close()
os.environ["TBRICKS_ADMIN_CENTER"] = original_admin_center

print("\n\nAlerts to be sent for following components:")

os.environ["TBRICKS_ADMIN_CENTER"] = original_admin_center

for component in generate_alert_for_components:
    print(component)