#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 20:23:00 2017

@author: zhoumeng  
"""
import pickle, time

class Decompress:
    def decompress(self, pkl_file, infile):
        decode_num = self.get_decode_num(pkl_file)
        self.decode_num_to_text(decode_num, infile)
    #load the dicitonary from pkl file
    def get_decode_num(self, pkl_file):
        with open(pkl_file, 'rb') as file:
            decode_num = pickle.load(file)
        return decode_num
    def decode_num_to_text(self, decode_num, infile):
        with open(infile, 'rb') as file:
            all_hex = file.read()#will get a list will all b bits hex
            
        all_binary_list = []
        for num in all_hex:
            binary = bin(num).replace('0b', '')
            if len(binary)<8:# because if the num is 00000001  it will become 1 which lead to error position for decompressing
                offset = 8 - len(binary)
                for i in range(offset):
                    binary = '0'+binary
            all_binary_list.append(binary)
        all_binary = ''.join(all_binary_list)#restore the string into '11101110011111111011001110110001' without '0b' and get the right digital totally and correctly
        self.write_to_file(all_binary, decode_num)

    def write_to_file(self, all_binary, decode_num):
        index = 0#where we are
        position = 1#from will we are to find the next n binary numbers if they are matching the dictionary key
        symbols = []
        while True:
            binary = all_binary[index:position]#record the 0101 before calculate will improve the speed of our code from 0.64 to 0.54
            if binary not in decode_num:
                position += 1
            else:
                if decode_num[binary] == None:
                    break
                #remove the decode_num[all_binary[index:index+position]] and adjust the record of the index
                #the time consuming decreases from 0.93 to 0.65
                symbols.append(decode_num[binary])
                index = position
                position += 1
        with open('infile-decompressed.txt', 'w') as file:
            file.write(''.join(symbols))
                    
if __name__ == '__main__':
    t = time.time()
    decompress = Decompress()
    pkl_file = 'infile-symbol-model.pkl'
    infile = 'infile.bin'
    decompress.decompress(pkl_file, infile)
    print('This decompressing consumed', time.time() - t, 'seconds')
