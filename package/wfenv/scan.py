import os
import sys
import win32gui
import win32api
import win32
import win32process
import psutil
import win32service
import win32serviceutil
import win32lz

from pathlib import Path
import tempfile

from .signatures import *
from .colors import *


import win32con
import win32service

def get_active_services():
    resume = 0
    accessSCM = win32con.GENERIC_READ
    accessSrv = win32service.SC_MANAGER_ALL_ACCESS

    #Open Service Control Manager
    hscm = win32service.OpenSCManager(None, None, accessSCM)

    #Enumerate Service Control Manager DB
    typeFilter = win32service.SERVICE_WIN32
    stateFilter = win32service.SERVICE_ACTIVE

    statuses = win32service.EnumServicesStatus(hscm, typeFilter, stateFilter)

    return statuses



def winEnumHandler(hwnd, ctx):

    text = win32gui.GetClassName(hwnd)
    class_text = win32gui.GetWindowText(hwnd)
    
    current_signatures = detected_signatures + detected_runtime_signatures
    for signature in current_signatures:
        if signature.upper() in text.upper() or signature.upper() in class_text.upper():
            tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            process_name = psutil.Process(pid).exe()
            print(f'{colwarn("Warning! Sucpicious window")}: [{colwinname(text)}] [{colwinclass(class_text)}] -> [{colpath(process_name)}] -> \"{colsignature(signature)}\"')

already_detected = []

def scan_path(path, levels = 0):
    try:
        files = os.listdir(path)
        for child_path in files:
            full_path = path + '\\' + child_path
            is_detected = False
            for signature in detected_signatures:
                if signature.upper() in full_path.upper():
                    
                    if full_path not in already_detected and child_path not in exception_files:
                        print(f'{colwarn("Warning! Sucpicious path")}: [{colpath(full_path)}] -> \"{colsignature(signature)}\"')
                        already_detected.append(full_path)

                    is_detected = True
            if levels and not is_detected:
                if os.path.isdir(full_path):
                    scan_path(full_path, levels - 1)
    except:
        pass




def scan_main(argv=None):
    if argv is None:
        argv = sys.argv

    active_services = get_active_services()

    for (short_name, desc, status) in active_services:
        current_signatures = detected_signatures + detected_runtime_signatures
        for signature in current_signatures:
            if signature.upper() in short_name.upper() or signature.upper() in desc.upper():
                print(f'{colwarn("Warning! Sucpicious service")}: [{colwinname(short_name)}] [{colwinclass(desc)}] -> \"{colsignature(signature)}\"')

    win32gui.EnumWindows(winEnumHandler, None)
    
    pids = win32process.EnumProcesses()
    for pid in pids:
        try:
            process_name = psutil.Process(pid).exe()     
            current_signatures = detected_signatures + detected_runtime_signatures
            for signature in current_signatures:
                if signature.upper() in process_name.upper():
                    print(f'{colwarn("Warning! Sucpicious process")}: [{colpath(process_name)}] -> \"{colsignature(signature)}\"')

        except:
            pass



    desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    home_path = str(Path.home())

    scan_path(desktop_path, 1)
    scan_path(home_path, 1)
    scan_path(home_path + "\\Downloads", 2)
    scan_path("C:\\", 1)
    scan_path("C:\\windows\\system32", 1)
    scan_path(tempfile.gettempdir(), 1)
    

if __name__ == "__main__":
    sys.exit(scan_main(sys.argv))