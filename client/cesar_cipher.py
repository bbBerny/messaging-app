# client/cesar_cipher.py
CESAR_SHIFT = 3

def cesar_encrypt(text):
    result = ""
    for c in text:
        code = ord(c)
        if 32 <= code <= 126:
            shifted = code + CESAR_SHIFT
            if shifted > 126:
                shifted -= 95
            result += chr(shifted)
        else:
            result += c
    return result

def cesar_decrypt(text):
    result = ""
    for c in text:
        code = ord(c)
        if 32 <= code <= 126:
            shifted = code - CESAR_SHIFT
            if shifted < 32:
                shifted += 95
            result += chr(shifted)
        else:
            result += c
    return result
