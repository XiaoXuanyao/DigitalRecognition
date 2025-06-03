
import hashlib



class Encryption():

    def sha256(mes:str):
        hashobject = hashlib.sha256(mes.encode())
        hexdig = hashobject.hexdigest()
        return hexdig