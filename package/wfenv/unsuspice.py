import os
import sys
import win32gui
import win32api
import win32
import win32process
import psutil
from termcolor import colored
from pathlib import Path
import tempfile

from .signatures import *
from .colors import *

import win32con
import win32service
import win32serviceutil

import signal

windows_to_close = []
pids_to_close = []
services_to_stop = []

def winEnumHandler(hwnd, ctx):
    text = win32gui.GetClassName(hwnd)
    class_text = win32gui.GetWindowText(hwnd)
    
    current_signatures = detected_signatures + detected_runtime_signatures
    for signature in current_signatures:
        if signature.upper() in text.upper() or signature.upper() in class_text.upper():
            tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            process_name = psutil.Process(pid).exe()
            print(f'{colwarn("Sucpicious window")}: [{colwinname(text)}] [{colwinclass(class_text)}] -> [{colpath(process_name)}] -> \"{colsignature(signature)}\"')
            if hwnd not in windows_to_close:
                windows_to_close.append(hwnd)
            if pid not in pids_to_close:
                pids_to_close.append(pid)



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

def unsuspice_main(argv=None):
    if argv is None:
        argv = sys.argv
    
    pids = win32process.EnumProcesses()
    for pid in pids:
        try:
            process_name = psutil.Process(pid).exe()     
            current_signatures = detected_signatures + detected_runtime_signatures
            for signature in current_signatures:
                if signature.upper() in process_name.upper():
                    print(f'{colwarn("Warning! Sucpicious process")}: [{colpath(process_name)}] -> \"{colsignature(signature)}\"')
                    if pid not in pids_to_close:
                        pids_to_close.append(pid)
        except:
            pass

    win32gui.EnumWindows(winEnumHandler, None)

    active_services = get_active_services()

    for (short_name, desc, status) in active_services:
        current_signatures = detected_signatures + detected_runtime_signatures
        for signature in current_signatures:
            if signature.upper() in short_name.upper() or signature.upper() in desc.upper():
                print(f'{colwarn("Warning! Sucpicious service")}: [{colwinname(short_name)}] [{colwinclass(desc)}] -> \"{colsignature(signature)}\"')
                services_to_stop.append(short_name)

    if len(pids_to_close) + len(services_to_stop) > 0:

        print('')
        print('Proceses to close:')
        for pid in pids_to_close:
            process_name = psutil.Process(pid).exe()
            print(f'{colwarn("!!!")} [{pid}] -> [{colpath(process_name)}] ')

        for sts in services_to_stop:
            print(f'{colwarn("!!!")} Service -> [{colpath(sts)}] ')

        result = input(f'{colwarn("!!!")} {len(pids_to_close)} processes and {len(services_to_stop)} services will be closed. Continue? [Y/N]: ')
        if result == 'Y' or result == 'y':
            for pid in pids_to_close:
                print('Terminating:', pid)
                p = psutil.Process(pid)
                p.terminate()
            for sts in services_to_stop:
                print('Stopping service:', sts)
                try:
                    win32serviceutil.StopService(sts)
                except:
                    pass           

            print('Finished.')
        else:
            print('Rejected.')
    else:
        print('Nothing to do.')


if __name__ == "__main__":
    sys.exit(unsuspice_main(sys.argv))


