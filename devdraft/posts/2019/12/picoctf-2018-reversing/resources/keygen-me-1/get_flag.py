#!/usr/bin/env python

def check_valid_char(char):
	if ord(char) >= ord('0') and ord(char) <= ord('9'): return 1
	elif ord(char) >= ord('A') and ord(char) <= ord('Z'): return 1
	return 0;


def my_ordi2(c):
    if c.isalpha():
        return ord(c) - ord('7')
    else:
        return ord(c) - ord('0')

def my_ord(char):
	if ord(char) >= ord('0') and ord(char) <= ord('9'):
		return int(char)- ord('0') # ord('0') = 48
        elif ord(char) >= ord('A') and ord(char) <= ord('Z'):
		return ord(char) - ord('7') #ord('7') = 0x30 = 55
        else:
            raise Exception("Bad character {}".format(char))

def check_valid_key(key):
    for i in range(len(key)):
	if (check_valid_char(list(key)[i])):
		continue
        else:
	    return 0
    return 1 

def vk(key):
    s = 0
    for i in range(len(key)-1):
        #print s
        s += ( my_ord(key[i]) + 1 )*( i + 1 )
    #print 's=',s
    #print 's%36=',s%36
    #print 'my_ord(key[-1])',my_ord(key[-1])
    return (s % 36) == my_ord(key[-1])

def validate_key2(key):
    var_14h = 0
    var_ch = len(key)
    for i in range(len(key)-1):
	#eax = key[i]
	edx = my_ord(key[i])+1
	eax = i + 1
	var_14h += eax * edx
    #for loop is equivalent to var_14h = ( my_ord(key[i] + 1 )( i + 1 )

    #BELOW CODE <=> ecx = var_14h % 36 --> via magic_number=0x38e38e39
    ecx = var_14h
    edx = 0x38e38e39
    eax = ecx
    edx = edx * eax
    ebx = edx
    #ebx = var_14h * 0x38e38e39
    ebx = int(ebx >> 32) # needed only for python, mul puts lower bytes in eax, higher in edx
    ebx = ebx >> 3

    eax = ebx << 3
    eax += ebx
    eax = eax << 2
    ecx = var_14h - eax   
    #ABOVE CODE <=> ecx = var_14h % 36 --> via magic_number=0x38e38e39 
    
    ebx = ecx
    edx = len(key)-1
    #eax= key[-1] ;  key[len(key_-1]	#last character
    #eax = my_ord(key[-1])
    print 'ecx='+str(ecx) + ' \t ' +  str(my_ord(key[-1])) + ' \t ' + str(ecx == my_ord(key[-1]))
    return ecx == my_ord(key[-1])

import logging
import re

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(filename='myapp.log', level=logging.INFO)

def validate_key(key):
    logging.info("Validating key: {}".format(key))
    if len(key) != 16:
        raise Exception("Bad length")
    if not re.match('^[A-Z0-9]+$', key):
        raise Exception("Bad characters")
    
    s = 0
    for i in range(len(key) - 1):
        edx = my_ord(key[i]) + 1
        eax = i + 1
        s += (edx * eax)

    ebx = 0x38E38E39 * s
    ebx = int(ebx >> 32) # needed only for python, mul puts lower bytes in eax, higher in edx
    ebx = ebx >> 3
    eax = ebx << 3
    eax += ebx
    eax = eax << 2
    ecx = s - eax

    logging.info("ecx: {}".format(hex(ecx)))
    my_ord_key_1 = my_ord(key[-1])
    if my_ord_key_1 is None:
        logging.info("ord(key[-1]): None")
    else:
        logging.info("ord(key[-1]): {}".format(hex(int(my_ord(key[-1])))))


    return ecx == my_ord(key[-1])


print check_valid_key('AAAAAAAAAA')
print check_valid_key('A@@A')


#We need last key character to match ecx == my_ord([key-1])
key = ''
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

#i = 0
print 'Bruteforce key'
from itertools import product
keys_iterator = product(alphabet, repeat = 16)
for k in keys_iterator:
    key = ''.join(k)
    if vk(key):
        print key
        break


print key, check_valid_key(key)
exit()


print "---------------->", key 
print vk('AAAAAAAAAAAAAAAO')
print "---------------->", key 
print validate_key('AAAAAAAAAAAAAAAO')
print "---------------->", key 
print validate_key2('AAAAAAAAAAAAAAAO')
print "---------------->", key 
#print check_valid_char('9')
#print check_valid_char('Z')
#print check_valid_char('}')

#for i in list(alphabet):

#for i in list(alphabet):
#    print i + '\t' + str(validate_key('AAAAAAAAAAAAAA'+i))
#    if validate_key('AAAAAAAAAAAAAA'+i):
#        print 'AAAAAAAAAAAAAA'+i
#        break
