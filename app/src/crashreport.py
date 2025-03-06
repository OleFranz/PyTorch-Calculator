import src.variables as variables
import src.console as console
import ctypes

RED = "\033[91m"
NORMAL = "\033[0m"

def CrashReport(Type:str, Message:str, Additional=None):
    if Message.strip() == "":
        return
    console.RestoreConsole()
    while Message.endswith('\n'):
        Message = Message[:-1]
    if variables.DevelopmentMode == False:
        Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
    print(f"{RED}{Type}{NORMAL}\n{Message}\n")