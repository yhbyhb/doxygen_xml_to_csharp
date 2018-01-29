
# coding: utf-8

# In[ ]:

from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from pprint import pprint
import re
import codecs
import json
import os

def shape_element(element):
    node = {}
    # Allows only three basic top level elements
    if element.tag in ('memberdef'):
        node["kind"] = element.attrib["kind"]
#         print element.attrib["kind"]

        if element.attrib["kind"] != "function": 
            return node

        params = []
        for child in element:
            if child.tag == "name":
                node["name"] = child.text
                # print node["returns"]

            if child.tag == 'definition':
                node["returns"] = child.text.split()[0]

            if child.tag == "argsstring":
                try:
                    argStr = re.sub(r'[\(\)]', '', child.text)
                    # print argStr
                    args = argStr.split(",")
                    for arg in args:
                        param = {}

                        index = arg.rfind("*")
                        if index == -1:
                            index = arg.rfind(" ")

                        if index != -1:
                            param["type"] = arg[:index+1].strip()
                            param["declname"] = arg[index+1:].replace("const", "").strip()
                        # print "type:", param["type"], "name:", param["declname"], index
                            params.append(param)
                except Exception:
                    print(ET.tostring(element))

        detaileddescription = []
        descNode = element.find("detaileddescription")

        detail = {}
        descriptions = []
        param_descs= []

        for para in descNode:
            desc = para.text
            if desc != None:
                descriptions.append(para.text.strip())

            parameterlist = para.find("parameterlist")
            if parameterlist != None:
                for parameteritem in parameterlist:
                    paramItemDic = {}
                    if parameteritem.tag == "parameteritem":
                        paramItemDic["name"] = parameteritem[0][0].text
                        paramItemDic["desc"] = parameteritem[1][0].text.strip()
                    param_descs.append(paramItemDic)

            simplesect = para.find("simplesect")
            if simplesect != None:
                returnStr = ""
                if simplesect[0].text:
                    returnStr = simplesect[0].text.strip()
                detail["returns"] = returnStr

        detail["summary"] = descriptions
        detail["params"] = param_descs

        node["detaileddescription"] = detail
        node["params"] = params

    return node

def process_xml(file_in, pretty = False):
    file_out = "{0}.json".format(os.path.splitext(os.path.basename(file_in))[0])
    data = []
    # iterative parsing and writing JSON file
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    file_in = 'nppi__linear__transforms_8h.xml'
    data = process_xml(file_in, True)
    pprint(data)

if __name__ == '__main__':
    import sys
    file_in = 'nppi__linear__transforms_8h.xml'
    print('Argument List:', str(sys.argv))
    if len(sys.argv) < 2:
        print('usage : python parse_doxygen_xml.py "filename.xml"')
    else:
        file_in = sys.argv[1]
        if os.path.isfile(file_in):
            data = process_xml(file_in, True)
        else:
            print('{} is not exist'.format(file_in))
