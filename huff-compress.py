#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 21:32:17 2017

@author: zhoumeng
\
------------------------------------------------------------
OPTIONS:
    -h : print this help message
    -s : the minimum element is ----'char' if 'char' following -s
         or 'word' if 'word' following -s  
------------------------------------------------------------\
"""

import sys, getopt, re, os, operator, pickle, array, time

class CommandLine:
    def __init__(self):
        opts, args = getopt.getopt(sys.argv[1:],'hs:')
        opts = dict(opts)

        if '-h' in opts:
            self.printHelp()
            

        if len(args) > 0:
            if os.path.exists(args[0]):
                self.infile = args[0]
            else:
                print('cannot find this file', file=sys.stdout)#no matter if there is 'file=sys.stdout' it could work
        else:
            print('please choose a file to compress', file=sys.stdout)
            sys.exit()
        
        if '-s' in opts:
            if opts['-s'] == 'char':
                self.element = 'char'
            elif opts['-s'] == 'word':
                self.element = 'word'
            else:
                self.printHelp()
        else:
            self.printHelp()##if no this line there will be an error about no element
            
    def printHelp(self):
        print(__doc__, file=sys.stderr)
        sys.exit()
        
#according to the element to choose a right method to compress

class Compress:
    
    class node:# for binary tree
        def __init__(self, probability, symbol=None, left=None, right=None, father=None):
            self.probability = probability
            self.symbol = symbol
            self.left = left
            self.right = right
            self.father = father
            
            
    def compress(self, element, infile):
        if element == 'char':
            self.char_compress(infile)
        if element == 'word':
            self.word_compress(infile)
    '''
    1 count every item's probability
    2 build a tree
    3 get every item's encode num
    4 encode file, note change the string into binary num
    '''       
    def char_compress(self, infile):
        #get the probability for every char
        char_prob = self.char_get_prob(infile)
        #get a sorted list with every char the probability is from high to low
        sorted_char = self.sorted_result(char_prob)
        #creat a list with leaf node
        leaf_node = self.change_symbol2node(sorted_char)
        #creat a binary tree and get the encode num of every symbol
        #t = time.time()
        encode_num = self.create_tree_and_get_encodeNum(leaf_node)
        #print('build the symbol model cost', time.time()-t, 'seconds')
        #get 0s 1s string, for all the symbol
        #tt = time.time()
        zeros_ones = self.get_char_zeros_ones(infile, encode_num)
        #a loop for changing every 8 chars into a binary 
        #and think about how to deal with if the lastest is lower than 8 
        self.put_zos_into_file(zeros_ones)
        #print('encode the input fime under the symbol mode cost', time.time()-tt, 'seconds')
                   
    def word_compress(self, infile):
        ##get the probability for every char
        word_prob = self.word_get_prob(infile)
        #get a sorted list with every char the probability is from high to low
        sorted_word = self.sorted_result(word_prob)
        #creat a list with leaf node
        leaf_node = self.change_symbol2node(sorted_word)
        #creat a binary tree and get the encode num of every symbol
        #t = time.time()
        encode_num = self.create_tree_and_get_encodeNum(leaf_node)
        #print('build the symbol model cost', time.time()-t, 'seconds')
        #get 0s 1s string, for all the symbol
        #tt = time.time()
        zeros_ones = self.get_word_zeros_ones(infile, encode_num)
        #put into file
        self.put_zos_into_file(zeros_ones)
        #print('encode the input fime under the symbol mode cost', time.time()-tt, 'seconds')
    
    #this method is for these two compressing ways
    def put_zos_into_file(self, zeros_ones):
        offset = 8 - len(zeros_ones)%8#if there is not enough digitals in one string, we need to change it to a 8 lenghts string via adding 0 at the left of it
        if offset!=0:
            lack_str = ''
            for i in range(0,offset):
                lack_str += '0'# if use zeros_ones + '0' maybe product some string with lenght = len(zeros_ones) - 1 or 2 or 3...
            zeros_ones += lack_str
        code_array = array.array('B')
        index = 0
        while index<len(zeros_ones):
            end_index = index + 8
            c = zeros_ones[index:end_index]
            code_array.append(int(c, 2))
            index = end_index
        with open('infile.bin', 'wb') as file:
            code_array.tofile(file)
    
    #this method for char-compressing way
    def get_char_zeros_ones(self, infile, encode_num):
        zeros_ones = []
        with open(infile) as file:
            for line in file:
                #l = list(line)
                for char in line:
                    zeros_ones.append(encode_num[char])
        zeros_ones.append(encode_num[None])#add a EOF at the end of this string
        return ''.join(zeros_ones)
    #this method for word-compressing way
    def get_word_zeros_ones(self, infile, encode_num):
        zeros_ones = []
        with open(infile) as file:
            re_word = re.compile('[a-zA-Z]+|[0-9]{1}|\W{1}|_{1}')
            for line in file:
                l_word = re_word.findall(line)
                for word in l_word:
                    zeros_ones.append(encode_num[word])
        zeros_ones.append(encode_num[None])#add a EOF at the end of this string
        return ''.join(zeros_ones)
    
    #special for char compressing, get the symbol with probability   
    def char_get_prob(self, infile):
        char_prob = {}# {char : occuring times} finally make occuring times divide the total char occuring times
        total_char = 0
        with open(infile) as file:
            for line in file:
                #line = line.lower() because i find that if we ignore the upper and lower, we cannot decode them correctly   
                #l = list(line)
                for char in line:
                    total_char += 1
                    if char in char_prob:
                        char_prob[char] += 1
                    else:
                        char_prob[char] = 1
        
        for char in char_prob.keys():
            char_prob[char] /= total_char 
        return char_prob
    #special for word compressing, get the symbol with probability 
    def word_get_prob(self, infile):
        word_prob = {}
        total_word = 0
        with open(infile) as file:
            re_word = re.compile('[a-zA-Z]+|[0-9]{1}|\W{1}|_{1}')
            for line in file:
                l_word = re_word.findall(line)
                for word in l_word:
                    total_word += 1
                    if word in word_prob:
                        word_prob[word] += 1
                    else:
                        word_prob[word] = 1
        for word in word_prob.keys():
            word_prob[word] /= total_word 
        return word_prob
#######################################################################################
    '''code in this piece is a series of functions with strong link among them
       This comment must align to the def code line...otherwise will throw an error'''
    #this method could be used by these tow compress ways
    def create_tree_and_get_encodeNum(self, leaf_node):
        nodes = leaf_node[:]#cannot use leaf_node, after iteration, leaf_node will be only 1 item list
        while len(nodes)!=1:
            a,b = nodes.pop(), nodes.pop()
            new_node = Compress.node(a.probability+b.probability, left=a, right=b)
            a.father = new_node
            b.father = new_node
            self.put_node_into_list(nodes, new_node)#put node into list and sort it
        root_node = nodes[0]# use this to judge if we get the root node to avoid the loss precision when we add two float numbers togther
        encode_num = self.get_encodeNum(leaf_node, root_node)
        return encode_num
    #return a dictionary
    def get_encodeNum(self, leaf_node, root_node):
        encode_num = {}# {node:num}
        decode_num = {}# {num:node}
        for node in leaf_node:
            num = []#need to reverse at the end
            temp = node
            while temp!=root_node:
                if temp.father.left == temp:#shows temp is a left child
                    num.append('0')
                else:
                    num.append('1')
                temp = temp.father
            num.reverse()
            codeNum = ''.join(num)
            encode_num[node.symbol] = codeNum#must add node.symbol, it make us could encode using this dictionary
            decode_num[codeNum] = node.symbol
        #to save the decode_num
        self.save_decode_num(decode_num)
        return encode_num
    #save the decode_num as a binary file
    def save_decode_num(self, decode_num):
        with open('infile-symbol-model.pkl', 'wb') as output:
            pickle.dump(decode_num, output)
    #use binary sort to put node into list
    def put_node_into_list(self, leaf_node, new_node):
        if len(leaf_node)==0:# the last time the list is empty
            leaf_node.append(new_node)
            return
        left, right = 0, len(leaf_node)-1
        middle = int(len(leaf_node)/2)
        while left < right:
            if leaf_node[middle].probability < new_node.probability:
                right = middle - 1
                middle = int((left+right)/2)
            else:
                left = middle + 1
                middle = int((left+right)/2)
        if leaf_node[right].probability <= new_node.probability :
            leaf_node.insert(left, new_node)
        else:
            leaf_node.insert(left+1, new_node)#because when we insert item into list, it will insert before the index, if the item is lower than the one on this index, we need to insert after this index so add 1
#######################################################################################
    #this method could be used by these tow compress ways
    def change_symbol2node(self, prob):#prob is a list of all symbol with their probabilities
        leaf_node = []
        for sym_prob in prob:
            leaf_node.append(Compress.node(sym_prob[1], symbol=sym_prob[0]))
        leaf_node.append(Compress.node(0, symbol=None))
        return leaf_node  
    
    #this method could be used by these tow compress ways
    def sorted_result(self, prob):#prob is a dict of all symbol with their probabilities
        return sorted(prob.items(), key=operator.itemgetter(1),reverse=True)

    
if __name__ == '__main__':
    config = CommandLine()
    t = time.time()
    com = Compress()
    com.compress(config.element, config.infile)
    print('This compressing consumed', time.time() - t, 'seconds')
