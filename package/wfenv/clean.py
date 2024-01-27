import winreg
import os
import shutil
import tempfile
import errno
from termcolor import colored
import winreg
import sys
from pathlib import Path

def RegFindValue(key, name):
    try:
        count = 0
        while 1:
            nname, value, type = winreg.EnumValue(key, count)
            if nname == name:
                return (nname, value, type)
            count = count + 1
    except WindowsError:
        pass

# def RegFindKey(key, name):
#     try:
#         count = 0
#         while 1:
#             nname, value, type = winreg.EnumValue(key, count)
#             if nname == name:
#                 return (nname, value, type)
#             count = count + 1
#     except WindowsError:
#         pass

def colpath(str):
    return colored(f'{str}', "light_magenta")

def get_warface_directory():
    aReg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    aKey = winreg.OpenKey(
        aReg, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\gcgame_0.1177')
    for i in range(40):
        try:
            val = winreg.EnumValue(aKey, i)
            if (val[0] == 'InstallLocation'):
                installLocation = val[1]
                return installLocation #[:len(installLocation) - 1]
        except EnvironmentError as ex:
            print(ex)
            break
    return None

def get_gc_directory():
    return os.getenv('LOCALAPPDATA') + '\\GameCenter'

def get_recent_folder():
    home_path = str(Path.home())
    return home_path + '\\Recent'


def silentremove(filename, logging = True):
    try:
        os.remove(filename)
        if logging:
            print(f'removed: "{colpath(filename)}"')
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred  

def remove_files_in_folder(path, remove_dirs = True):
    removed_some = False
    try:
        files = os.listdir(path)
        for child_path in files:
            full_path = path + '\\' + child_path
            try:
                if os.path.isdir(full_path):
                    if remove_dirs:
                        shutil.rmtree(full_path, ignore_errors=True)
                else:
                    silentremove(full_path, False)
            except Exception as ex:
                pass

            if not os.path.exists(full_path):
                removed_some = True
    except Exception as ex:
        pass

    if removed_some:
        print(f'removed files in "{ colpath(path) }"')

def remove_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
        print(f'removed folder: "{ colpath(path) }"')

def get_system_temp_dir():
    aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    aKey = winreg.OpenKey(aReg, 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment')
    for i in range(1024):
        try:
            idk = winreg.EnumValue(aKey, i)
            if idk[0] == 'TEMP':
                return idk[1]
        except EnvironmentError:
            break
    return None


def clear_recent():
    recent_dir = get_recent_folder()
    automatic_destinations = recent_dir + '\\AutomaticDestinations'
    custom_destinations = recent_dir + '\\CustomDestinations'
    remove_files_in_folder(recent_dir, False)
    remove_files_in_folder(automatic_destinations, False)
    remove_files_in_folder(custom_destinations, False)

def clear_prefetch():
    windir = os.getenv('windir')
    if not windir:
        print('windir folder not found')
        return
    
    prefetch_dir = windir + '\\Prefetch'
    if os.path.exists(prefetch_dir):
        remove_files_in_folder(prefetch_dir)
    else:
        print(f'folder does not exist: "{prefetch_dir}"')

def clear_services():
    tmpdir = tempfile.gettempdir()
    aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    
    aKey = winreg.OpenKey(aReg, 'SYSTEM\\CurrentControlSet\\Services\\')
    suspicious_services : list = []

    # list all values for a key
    try:
        count = 0
        while 1:
            name = winreg.EnumKey(aKey, count)
            regpath = 'SYSTEM\\CurrentControlSet\\Services\\' + name + '\\'
            bKey = winreg.OpenKey(aReg, regpath)

            value = RegFindValue(bKey, 'ImagePath')
            if value:
                if tmpdir in value[1]:
                    suspicious_services.append((regpath, name, value[1]))
                    # print(f'driver: {regpath} -> {name} -> {value[1]}')  

            

            count = count + 1
    except WindowsError:
        pass
    
    for svc in suspicious_services:
        try:
            winreg.DeleteKey(aReg, svc[0])
            print(f'removed service: "{colpath(svc[0])}" -> "{colpath(svc[1])}" -> "{colpath(svc[2])}"')
        except WindowsError as e:
            print(f'Failed to remove "{colpath(svc[0])}":', e)

def clean_main(argv=None):
    if argv is None:
        argv = sys.argv

    bFull = '--full' in argv or '-f' in argv

    warface_dir = get_warface_directory()

    gc_dir = get_gc_directory()
    temp_dir = tempfile.gettempdir()

    if bFull:
        silentremove(gc_dir + '\\bu.state')
        silentremove(gc_dir + '\\GameCenter.ini')
        silentremove(gc_dir + '\\configMirrors.xml')
        silentremove(gc_dir + '\\Chrome.log')
        silentremove(gc_dir + '\\configMainRepository.xml')
        silentremove(gc_dir + '\\configBigGames.xml')
        silentremove(gc_dir + '\\configIPSpec.xml')
        silentremove(gc_dir + '\\main.log')
    else:
        print('[Cleaner] GameCenter logs and settings are ignored (use -f or --full flag to clean it).')

    silentremove(warface_dir + '\\Game.log')
    silentremove(warface_dir + '\\server_profile.txt')
    silentremove(warface_dir + '\\imgui.ini')

    remove_folder(warface_dir + '\\LogBackups')
    remove_files_in_folder(temp_dir)

    silentremove('C:\\Windows\\Temp\\mracdrv.log')
    silentremove('C:\\Windows\\Temp\\mrac.log')

    silentremove(get_system_temp_dir() + '\\mracdrv.log')
    silentremove(get_system_temp_dir() + '\\mrac.log')

    clear_recent()
    clear_prefetch()
    clear_services()

    print('[Cleaner] Work is finished')

if __name__ == "__main__":
    sys.exit(clean_main(sys.argv))