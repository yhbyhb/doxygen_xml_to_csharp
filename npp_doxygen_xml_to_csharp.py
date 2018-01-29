import os
import parse_doxygen_xml
import re

header1 = """\
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using Npp8u = System.Byte;
using Npp8s = System.SByte;
using Npp16u = System.UInt16;
using Npp16s = System.Int16;
using Npp32u = System.UInt32;
using Npp32s = System.Int32;
using Npp64u = System.UInt64;
using Npp64s = System.Int64;
using Npp32f = System.Single;
using Npp64f = System.Double;

namespace CSCuda.NPP
{
    public partial class Npp"""

header2 = """
    {
"""

footer = """\
    }
}"""

defaultIndentStr = '    '
dllImportStr = '[DllImport(dllFileName, SetLastError = true)]\n'
accessorStr = 'public static extern'

files = [f for f in os.listdir('.') if os.path.isfile(f)]
# files = [
#             # 'nppi__arithmetic__and__logical__operations_8h.xml',
#             # 'npps__support__functions_8h.xml',
#             # 'nppcore_8h.xml',
#             # "nppi__data__exchange__and__initialization_8h.xml",
#             "nppi__geometry__transforms_8h.xml"
#          ]

for f in files:
    filename, file_extension = os.path.splitext(f)

    if file_extension != '.xml': continue
    findex = filename.find('npp')
    if findex != 0: continue

    header = header1 + filename[findex+3] + header2

    print('convert {} --> {}{}'.format(f, filename, '.json'))
    data = parse_doxygen_xml.process_xml(f, True)

    cs_filename = filename.replace("__", "_").replace("_8h", "")
    with open("{}.cs".format(cs_filename), "w") as text_file:
        text_file.write(header)
        for item in data:
            if item['kind'] != 'function':
                continue
            returnTypeStr = item["returns"]
            if "*" in returnTypeStr:
                # print returnTypeStr
                returnTypeStr = "IntPtr"

            paramsStr = []
            for param in item["params"]:
                paramTypeStr = param["type"]
                paramNameStr = param["declname"]
                paramTypeStr = paramTypeStr.replace("const ", "")
                # print "type:", paramTypeStr, "name:", paramNameStr
                if "*" in paramTypeStr:
                    paramTypeStr = "IntPtr"
                index = paramNameStr.find("[")
                if index != -1:
                    # print paramNameStr[index+1:index+2]
                    # print paramNameStr[:index]
                    paramTypeStr = "[MarshalAs(UnmanagedType.LPArray, SizeConst = {})]{}[]".format(paramNameStr[index+1:index+2], paramTypeStr)
                    paramNameStr = paramNameStr[:index]
                paramStr = defaultIndentStr * 3 + " ".join([paramTypeStr, paramNameStr])
                paramsStr.append(paramStr)

            comment_dict = item['detaileddescription']
            comment_summaries = comment_dict['summary']
            comment_params = comment_dict['params']

            text_file.write(defaultIndentStr * 2 + "/// <summary>\n")
            for summary in comment_summaries:
                text_file.write(defaultIndentStr * 2 + "/// " + summary +"\n")
            text_file.write(defaultIndentStr * 2 + "/// </summary>\n")
            for comment_param in comment_params:
                text_file.write(defaultIndentStr * 2 + '/// <param name="{}">{}</param>\n'.format(comment_param["name"], re.sub(r'[\<\>]', '"', comment_param['desc'])))
            comment_return_str = ""
            if 'returns' in comment_dict:
                comment_return_str = comment_dict['returns']
            text_file.write(defaultIndentStr * 2 + "/// <returns>{}</returns>\n".format(comment_return_str))

            text_file.write(defaultIndentStr * 2 + dllImportStr)
            text_file.write(defaultIndentStr * 2 + "{} {} {}(".format(accessorStr, returnTypeStr, item["name"]))
            if len(paramsStr) > 0:
                text_file.write("\n" + ",\n".join(paramsStr))
            text_file.write(");\n\n")

        text_file.write(footer)

    print('convert {0}{1} --> {0}{2}'.format(filename, '.json', '.cs'))
