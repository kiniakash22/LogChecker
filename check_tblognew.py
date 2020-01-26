import xml.dom.minidom

doc = xml.dom.minidom.parse("configuration.xml")

component_types = doc.getElementsByTagName("component")

for component in component_types:
        print(component.getAttribute("type"))