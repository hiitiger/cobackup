import win32api
from win32api import  HIWORD, LOWORD, HIWORD, LOWORD

def get_version_number(filename):
    try:
        info = win32api.GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)
    except:
        return 0, 0, 0, 0

def version_to_str(versoin):
    return '.'.join([str(i) for i in versoin])


#print(get_version_number("C:\\Windows\\notepad.exe"))