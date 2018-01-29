import os
import parse_doxygen_xml

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    filename, file_extension = os.path.splitext(f)

    if file_extension != '.xml': continue
    if filename.find('npp') != 0: continue

    print('convert {} --> {}{}'.format(f, filename, '.json'))
    data = parse_doxygen_xml.process_map(f, True)
