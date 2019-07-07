#!/bin/env python3

'''
 Yet Another Photo Catalog
 Author: Stanislav V. Emets
 e-mail: emetssv@mail.ru 

'''
import sys, os, exifread, stat
from getopt import getopt, GetoptError
from datetime import datetime
import shutil

# globals
always_yes = False
clean_source = False
#

ACTION_NONE = 0
ACTION_CREATE = 1
ACTION_ADD = 2
ACTION_IMPORT = 3

DO_ACTION = ACTION_NONE
ACTION_PARAMS = ""

CATALOG_PATH = ""


def print_help():
    print("Yet Another Photo Catalog (c) 2016 Stanislav V. Emets")
    print("Usage:")
    print("    yapc [OPTIONS] </path/to/photo_catalog>")
    print("Options:")
    print("    -c | --create - create new catalog")
    print("    -a </path/to/file> | --add=</path/to/file> - add new file to catalog")
    print("    -i </path/to/folder> | --import=</path/to/folder> - import photos to catalog")
    print("    -d | --del - delete files after add or import")
    print("    -y | --yes - answer yes to all actions")


def parse_args():
    global DO_ACTION, ACTION_NONE, ACTION_CREATE, ACTION_ADD, ACTION_IMPORT, always_yes, clean_source, ACTION_PARAMS, CATALOG_PATH

    exit_status = True

    try:
        opts, args = getopt(sys.argv[1:], "hca:i:dy", ["help", "create", "add=", "import=", "del", "yes", ])
    except GetoptError:
        return False

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            exit_status = False
        elif opt in ("-c", "--create"):
            if DO_ACTION == ACTION_NONE:
                DO_ACTION = ACTION_CREATE
            else:
                exit_status = False
        elif opt in ("-a", "--add"):
            if DO_ACTION == ACTION_NONE:
                DO_ACTION = ACTION_ADD
                ACTION_PARAMS = os.path.expanduser(arg.strip())
            else:
                exit_status = False
        elif opt in ("-i", "--import"):
            if DO_ACTION == ACTION_NONE:
                DO_ACTION = ACTION_IMPORT
                ACTION_PARAMS = os.path.expanduser(arg.strip())
            else:
                exit_status = False
        elif opt in ("-d", "--del"):
            clean_source = True
        elif opt in ("-y", "--yes"):
            always_yes = True

    if len(args) > 0:
        CATALOG_PATH = os.path.expanduser(args[0].strip())
    else:
        exit_status = False

    return exit_status


def is_catalog(p_path):
    if not os.path.isdir(p_path):
        return False
    if os.path.isfile(os.path.join(p_path, ".yapc")):
        return True
    else:
        return False


def create_catalog(p_path):
    if is_catalog(p_path):
        print("Path", p_path, "already yet another photo catalog!")
        return False  # todo: need create error codes

    if os.path.isdir(p_path):
        catalog_desc = open(os.path.join(p_path, ".yapc"), "w")
        catalog_desc.close()
        print("Catalog successfully created!")
    else:
        print("Path", p_path, "not found!")
        return False


def add_to_catalog(p_catalog, p_path):
    if not is_catalog(p_catalog):
        print(p_path, "not yet another photo catalog")
        return False

    if os.path.isfile(p_path):  # regular file, add to catalog
        img = open(p_path, 'rb')
        exif_tags = exifread.process_file(img)
        img.close()
        date_original = ''
        try:
            date_original = str(exif_tags['EXIF DateTimeOriginal'])
            date_original = date_original.split(sep=' ')[0]
        except KeyError:
            pass
        
        if not date_original.strip():
            file_attr = os.stat(p_path)
            if stat.S_ISREG(file_attr.st_mode):
                date_original = datetime.fromtimestamp(file_attr.st_ctime)
                date_original = date_original.strftime('%Y:%m:%d')
        
        print(date_original)
        if date_original != '':
            year, month, day = date_original.split(':')
        else:
            print(p_path)
                        
        # copy_path = os.path.join(p_catalog, year, month, day, os.path.basename(p_path))
        copy_path = os.path.join(p_catalog, year, month, day)
        
        if not os.path.isdir(copy_path):
            os.makedirs(copy_path, exist_ok = True)
            
        shutil.copy(p_path, os.path.join(copy_path, os.path.basename(p_path)))
        

    else:  # catalog, call import
        import_to_catalog(p_catalog, p_path)


def import_to_catalog(p_catalog, p_path):
    if os.path.isdir(p_path): 
        file_list = os.listdir(path=p_path)
        for file_name in file_list:
            file_name = os.path.join(p_path, file_name)
            add_to_catalog(p_catalog, file_name)
    else: # regular file, add to catalog
        add_to_catalog(p_catalog, p_path)


def main():
    if not parse_args():
        print("Missing args, please read help first.")
        print_help()

    # ok, we are ready for work

    if DO_ACTION == ACTION_CREATE:
        create_catalog(CATALOG_PATH)

    elif DO_ACTION == ACTION_ADD:
        add_to_catalog(CATALOG_PATH, ACTION_PARAMS)

    elif DO_ACTION == ACTION_IMPORT:
        import_to_catalog(CATALOG_PATH, ACTION_PARAMS)


if __name__ == '__main__':
    main()
