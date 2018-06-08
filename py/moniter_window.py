import sys
import ctypes
import ctypes.wintypes
import win32gui
import win32process
import win32con
import win32api

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)

def lowindow(hwnd):
    print('window {} => {}'.format(hwnd, win32gui.GetWindowText(hwnd)))


def def_win32_loop():
    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessageW(msg)
        user32.DispatchMessageW(msg)

def moniter_window_title(title):
    window = win32gui.FindWindow(None, title)
    if not window:
        print('not found window')
        sys.exit(1)
    lowindow(window)
    thread_id, process_id = win32process.GetWindowThreadProcessId(window)
    
    print('process_id {} thread_id {}'.format(process_id, thread_id))

    OBJID_WINDOW = 0
    CHILDID_SELF = 0
    def win_event_proc_cb(hook, event, hwnd, idObject, idChild, idEventThread, dwtime):
        if hwnd == window and event == win32con.EVENT_OBJECT_NAMECHANGE and idObject == OBJID_WINDOW  and idChild == CHILDID_SELF :
            lowindow(hwnd)

    ole32.CoInitialize(0)
    DWORD = ctypes.c_ulong
    win_event_proc = WinEventProcType(win_event_proc_cb)
    user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
    g_hook = user32.SetWinEventHook(
        win32con.EVENT_OBJECT_NAMECHANGE,
        win32con.EVENT_OBJECT_NAMECHANGE,
        0,
        win_event_proc,
        DWORD(process_id),
        DWORD(thread_id),
        win32con.WINEVENT_OUTOFCONTEXT
    )
    if not g_hook:
        print('SetWinEventHook failed error {}'.format(win32api.GetLastError()))
        sys.exit(1)
        
    print('g_hook {}, thread_id {}'.format(g_hook, thread_id))

    def_win32_loop()

    user32.UnhookWinEvent(g_hook)
    ole32.CoUninitialize()


def moniter_fg_window():
    def win_event_proc_cb(hWinEventHook, event, hwnd, idObject,
                     idChild, dwEventThread, dwmsEventTime):
        lowindow(win32gui.GetForegroundWindow())

    win_event_proc = WinEventProcType(win_event_proc_cb)

    user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
    hook = user32.SetWinEventHook(
        win32con.EVENT_SYSTEM_FOREGROUND,
        win32con.EVENT_SYSTEM_FOREGROUND,
        0,
        win_event_proc,
        0,
        0,
        win32con.WINEVENT_OUTOFCONTEXT | win32con.WINEVENT_SKIPOWNPROCESS
    )
    if hook == 0:
        print('SetWinEventHook failed')
        sys.exit(1)

    def_win32_loop()

    user32.UnhookWinEvent(hook)
    ole32.CoUninitialize()

moniter_fg_window()