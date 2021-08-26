import math
import random
import base64
from Crypto.Cipher import AES


def getRandomString(length):
    chs = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
    result = ''
    for i in range(0, length):
        result += chs[(math.floor(random.random() * len(chs)))]
    return result


def EncryptAES(s, key, iv='1' * 16, charset='utf-8'):
    key = key.encode(charset)
    iv = iv.encode(charset)
    BLOCK_SIZE = 16
    pad = lambda s: (s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE))
    raw = pad(s)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(bytes(raw, encoding=charset))
    return str(base64.b64encode(encrypted), charset)


def DecryptAES(s, key, iv='1' * 16, charset='utf-8'):
    key = key.encode(charset)
    iv = iv.encode(charset)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypt = unpad(cipher.decrypt(base64.b64decode(s)))
    return str(decrypt, charset)


def AESEncrypt(data, key):
    return EncryptAES(getRandomString(64) + data, key, getRandomString(16))


def AESDecrypt(data, key):
    return DecryptAES(data, key)[64:]
