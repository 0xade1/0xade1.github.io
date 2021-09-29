#!/usr/bin/env python
from Crypto.Cipher import DES
import datetime
import time
import random
import struct
import math

KEY_LENGTH = 8
BLOCK_SIZE = DES.block_size
FILE_CHUNK_SZ = 4096 # 4 KiB

def generate_key(seed):
    key = ''
    for i in range(0, KEY_LENGTH):
        seed = (214013*seed + 2531011) 
        key += chr(seed >> 16 & 0x7fffffff & 0xff)
    return key

#message has to be a multiple of 8, so we add the padding number at the end of the message
def pad(s):
    return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
            chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

def pad_size(s):
    if s is None or len(s) == 0:
        return 0
    last_byte = s[len(s)-1].encode('hex')
    if int(last_byte, 16) > 8:
            return 0
    return int(last_byte, 16)

def encrypt(seed, message):
    print(seed)
    key = generate_key(seed)
    print("key length {}".format(len(key)))
    iv = "00000000"
    cipher = DES.new(key, DES.MODE_CBC, iv)
    return cipher.encrypt(iv + pad(message))

def decrypt(seed, message):
    key = generate_key(seed)
    iv = message[:8]
    cipher = DES.new(key, DES.MODE_CBC, iv)
    dec = cipher.decrypt(message)
    pad_sz = pad_size(dec)
    #print("key={} iv={} pad_size={} dec={}".format(key.encode('hex'), iv.encode('hex'), pad_sz, dec.encode('hex')))
    if pad_sz == 0:
        return dec[8:]
    return dec[8:-pad_sz]

def entropy(string):
    string = string.encode('hex')
    prob = [ float(string.count(c)) / len(string) for c in dict.fromkeys(list(string)) ]
    entropy = - sum([ p * math.log(p) / math.log(2.0) for p in prob ])
    return entropy

'''
basetime is time around which we are bruteforcing
delta is the range of seconds we are  
'''
def bruteforce_encryption_time(filecontent, basetime, delta):
    global time
    closest = 2<<128
    besttime = 0
    bestplain = ""
    start = basetime - delta/2
    end = basetime + delta/2
    #dt_start = datetime.fromtimestamp(start).strftime("%d. %B %Y %I:%M%p")
    dt_start = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(int(start)))
    dt_end = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(int(end)))
    print("[+] Start time = {}".format(dt_start))
    print("[+] End time = {}".format(dt_end))
    print("[+] Trying every possible encryption time between %d and %d (in seconds since Epoch)" % (start, end))
    for time in range(start, end):
        #plain = decrypt(time, filecontent[:4096])
        plain = decrypt(time, filecontent)
        if len(plain) > 4096:
            dist = entropy(plain[:4096]) #only analyze the first 4KB of the file for randomness testing
        else:
            dist = entropy(plain) #only analyze the first 4KB of the file for randomness testing
        #print("seed: {0} entropy: {1} lenght:{2} decrypt ->: {3}".format(time, dist, len(plain), plain))
        if dist < closest:
            besttime = time
            bestplain = plain
            closest = dist
    print("\tBruteforce results:")
    print("\t"*2 + "Probable timestamp of the encryption date: %d" % besttime)
    print("\t"*2 + "Average entropy per byte: %s" % closest)
    print("\t"*2 + "Start of the decrypted file: %s" %repr(bestplain[:30]))
    return besttime

def get_file_content(filepath):
    content = ''
    with open(filepath, "rb") as infile:
        #chunk = infile.read(FILE_CHUNK_SZ)
        content = infile.read()
    return content

def get_encrypted_pdf_content():
    return get_file_content('ElfUResearchLabsSuperSledOMaticQuickStartGuideV1.2.pdf.enc')

def test():
    seed = int(time.time()-random.randrange(100))
    t = datetime.datetime(2019, 12, 6, 20, 0)
    basetime = int(time.time())-49
    delta = 100
    message = 'A'*33
    enc = encrypt(seed, message)
    besttime = bruteforce_encryption_time(enc, basetime, delta)
    print("-------------------")
    print("Original Seed: {} \tMessage: {}".format(seed, decrypt(seed, enc)))
    print("Bruteforced Seed: {} \tMessage: {}".format(besttime, decrypt(besttime, enc)))


def decrypt_pdf():
    enc = get_encrypted_pdf_content()
    hour = 20
    t = datetime.datetime(2019, 12, 6, 20, 0)
    basetime = int(time.mktime(t.timetuple()))
    delta = 2*60*60
    besttime = bruteforce_encryption_time(enc, basetime, delta)
    decrypted = decrypt(besttime, enc)
    with open("ElfUResearchLabsSuperSledOMaticQuickStartGuideV1.2.pdf", "wb") as out_file:
        out_file.write(decrypted)


#test()
decrypt_pdf()
