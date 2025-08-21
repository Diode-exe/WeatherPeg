import win32com.client
import threading
import pythoncom

speech_lock = threading.Lock()

def speaker(text):
    def _speak():
        with speech_lock:  # Only one speech at a time
            try:
                pythoncom.CoInitialize()
                speaker_obj = win32com.client.Dispatch("SAPI.SpVoice")
                speaker_obj.Speak(text)
            except Exception as e:
                print(f"Speech error: {e}")
            finally:
                try:
                    pythoncom.CoUninitialize()
                except:
                    pass
    
    thread = threading.Thread(target=_speak)
    thread.daemon = True
    thread.start()
    
def get_config_bool_tts(key):
    configfilename = "txt/config.txt"
    try:
        with open(configfilename, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key}:"):
                    value = line.split(":", 1)[1].strip()
                    # Convert to boolean (0 = False, 1 = True)
                    return value == "1"
    except FileNotFoundError:
        print(f"[LOG] File {configfilename} not found")
        return False
    return False  # Default to False if not found