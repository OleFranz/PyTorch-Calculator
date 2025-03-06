import src.variables as variables
import traceback

if variables.OS == "nt":
    import win32gui, win32con, win32console
    import ctypes

RED = "\033[91m"
NORMAL = "\033[0m"

def RestoreConsole():
    try:
        if variables.OS == "nt":
            if variables.ConsoleHWND != None and variables.ConsoleName != None:
                win32gui.ShowWindow(variables.ConsoleHWND, win32con.SW_RESTORE)
            else:
                variables.ConsoleName = win32console.GetConsoleTitle()
                variables.ConsoleHWND = win32gui.FindWindow(None, str(variables.ConsoleName))
                win32gui.ShowWindow(variables.ConsoleHWND, win32con.SW_RESTORE)
    except:
        Type = "\nConsole - Restore Error."
        Message = str(traceback.format_exc())
        while Message.endswith('\n'):
            Message = Message[:-1]
        if variables.DevelopmentMode == False:
            Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{Type}{NORMAL}\n{Message}\n")

def HideConsole():
    try:
        if variables.OS == "nt":
            if variables.ConsoleHWND != None and variables.ConsoleName != None:
                win32gui.ShowWindow(variables.ConsoleHWND, win32con.SW_HIDE)
            else:
                variables.ConsoleName = win32console.GetConsoleTitle()
                variables.ConsoleHWND = win32gui.FindWindow(None, str(variables.ConsoleName))
                win32gui.ShowWindow(variables.ConsoleHWND, win32con.SW_HIDE)
    except:
        Type = "\nConsole - Hide Error."
        Message = str(traceback.format_exc())
        while Message.endswith('\n'):
            Message = Message[:-1]
        if variables.DevelopmentMode == False:
            Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{Type}{NORMAL}\n{Message}\n")

def CloseConsole():
    try:
        if variables.OS == "nt":
            if variables.ConsoleHWND != None and variables.ConsoleName != None:
                ctypes.windll.user32.PostMessageW(variables.ConsoleHWND, 0x10, 0, 0)
            else:
                variables.ConsoleName = win32console.GetConsoleTitle()
                variables.ConsoleHWND = win32gui.FindWindow(None, str(variables.ConsoleName))
                ctypes.windll.user32.PostMessageW(variables.ConsoleHWND, 0x10, 0, 0)
    except:
        Type = "\nConsole - Close Error."
        Message = str(traceback.format_exc())
        while Message.endswith('\n'):
            Message = Message[:-1]
        if variables.DevelopmentMode == False:
            Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{Type}{NORMAL}\n{Message}\n")