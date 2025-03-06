from multiprocessing import Lock, shared_memory
import pickle
import json
import os


Path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))).replace("\\", "/") + "/"
SharedMemoryName = "PYTORCH-CALCULATOR-SETTINGS"
SharedMemorySize = 1024 * 1024
Lock = Lock()


try:
    SharedMemory = shared_memory.SharedMemory(name=SharedMemoryName, create=False)
except FileNotFoundError:
    SharedMemory = shared_memory.SharedMemory(name=SharedMemoryName, create=True, size=SharedMemorySize)
    with open(f"{Path}config/settings.json") as File:
        try:
            JSONData = json.load(File)
        except:
            JSONData = {}
        Data = pickle.dumps(JSONData)
    SharedMemory.buf[:len(Data)] = Data
    SharedMemory.buf[len(Data):] = b'\x00' * (SharedMemorySize - len(Data))


def ReadMemory():
    Data = bytes(SharedMemory.buf).rstrip(b'\x00')
    try:
        Settings = pickle.loads(Data)
    except Exception:
        Settings = {}
    return Settings


def WriteMemory(Settings):
    Data = pickle.dumps(Settings)
    if len(Data) > SharedMemorySize:
        raise ValueError("Settings exceed shared memory capacity")
    SharedMemory.buf[:len(Data)] = Data
    SharedMemory.buf[len(Data):] = b'\x00' * (SharedMemorySize - len(Data))


def SaveJSON(Settings):
    try:
        with open(f"{Path}config/settings.json", "w") as File:
            json.dump(Settings, File, indent=4)
    except:
        pass


def Get(Category:str, Name:str, Value:any=None):
    with Lock:
        Settings = ReadMemory()
        if Category in Settings and Name in Settings[Category]:
            return Settings[Category][Name]
        if Category not in Settings:
            Settings[Category] = {}
        if Name not in Settings[Category]:
            Settings[Category][Name] = Value
        WriteMemory(Settings)
        SaveJSON(Settings)
        return Settings[Category][Name]


def Set(Category:str, Name:str, Value:any):
    with Lock:
        Settings = ReadMemory()
        if Category not in Settings:
            Settings[Category] = {}
        Settings[Category][Name] = Value
        WriteMemory(Settings)
        SaveJSON(Settings)