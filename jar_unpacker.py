import zipfile
from sys import argv
from typing import List
from os import path, makedirs

PATH_PREFIX_STARTER : str = "tbl/"

def extract_motdm_assets(bytes_listing : bytearray, bytes_data : bytearray, path_output : str):
    try:
        str_data = bytes_listing.decode(encoding='ascii').strip()
    except UnicodeDecodeError:
        print("Failed to decode member table. Quitting...")
        return
    
    str_data = str_data.split("\n")
    if len(str_data) < 1:
        return
    
    try:
        count_files = int(str_data.pop(0))
    except ValueError:
        return
    
    if count_files != len(str_data):
        print("Warning: File listing does not reveal all files in member set.")
    count_files = min(count_files, len(str_data))

    list_f_name : List[str] = []
    list_f_off : List[int] = []
    
    for idx_file in range(count_files):
        name_off = str_data[idx_file].strip().split(",")
        if len(name_off) != 2:
            print("Warning: Failed to decode member listing, line %d = %s" % (idx_file, str_data[idx_file]))
            continue
        
        f_name, offset = name_off[0], name_off[1]
        if offset.isdigit():
            offset = int(offset)
            if offset < 0:
                print("Warning: Illegal offset. Skipped!")
                continue
        else:
            print("Warning: Offset type invalid. Skipped!")
            continue

        list_f_name.append(f_name)
        list_f_off.append(offset)            
        
    n_list = sorted(zip(list_f_off, list_f_name))
    count_files -= 1
    makedirs(path_output, exist_ok=True)

    for idx_member, member in enumerate(n_list):
        offset, name = member

        if idx_member == count_files:
            len_data = len(bytes_data) - offset
        else:
            len_data = n_list[idx_member + 1][0] - offset
        
        len_data = max(len_data, 0)

        with open(path.join(path_output, name), 'wb') as output:
            output.write(bytes_data[offset : offset + len_data])

def extract_jar(path_jarfile : str, path_output : str) -> bool:
    if zipfile.is_zipfile(path_jarfile):

        jar_extracted : bool = False
        enc_listing_member : bytearray = bytearray(b'')
        enc_listing_data : bytearray = bytearray(b'')

        try:
            with zipfile.ZipFile(path_jarfile, 'r') as modtm_zip:
                list_paths = modtm_zip.namelist()
                list_paths = [i[len(PATH_PREFIX_STARTER):] for i in sorted(list_paths) if i.startswith(PATH_PREFIX_STARTER) and i != PATH_PREFIX_STARTER]
                
                if len(list_paths) == 2:
                    enc_listing_member = bytearray(modtm_zip.read(PATH_PREFIX_STARTER + list_paths[0]))
                    enc_listing_data = bytearray(modtm_zip.read(PATH_PREFIX_STARTER + list_paths[1]))
                    jar_extracted = True
        except Exception as e:
            print("Failed to open JAR file. Quitting...")
            return False
        
        if jar_extracted:
            extract_motdm_assets(enc_listing_member, enc_listing_data, path_output)
            return True
        
    print("Failed to unpack JAR file. Quitting...")
    return False

if __name__ == "__main__":
    if len(argv) == 1:
        print("This script is for unpacking MotDM JAR files. Find them at your own discredition.")
        print("The archive needed is the JAR file inside the Games/<name>/bin folder.")
        print("\nUsage: ")
        print("\tpy <path_to_this> <path_to_jar> <optional:path_to_output_folder>")
        print("\n\t - If the output is not specified, a new folder will be created beside the JAR containing the files.")
    else:
        path_input = argv[1]
        if not(path.isabs(path_input)):
            path_input = path.abspath(path_input)

        if len(argv) > 2:
            path_output = path.normpath(argv[2])
            if not(path.isabs(path_output)):
                path_output = path.abspath(path_output)
        else:
            path_dir, name_jar = path.split(path_input)
            name_jar, _ext = path.splitext(name_jar)
            path_output = path.join(path_dir, name_jar)

        if extract_jar(path_input, path_output):
            print("Extraction completed! Files extracted at %s" % path_output)
        else:
            print("Extraction failed!")
