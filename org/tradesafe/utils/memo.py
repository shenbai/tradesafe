# coding:utf-8
'''
Created on 2016年6月19日

@author: tack
'''
import pickle

class Memo(object):
    '''
    memento 
    '''
    
    memory = {}
    init  = 0
    
    def __init__(self, params):
        '''
        memento
        '''
    
    @staticmethod
    def load():
        if Memo.init == 0:
            import os
            if os.path.exists('.memo'):
                Memo. memory = pickle.load(open('.memo', 'rb'))
            Memo.init = 1
            
    @staticmethod
    def save():
        output = open('.memo', 'wb')
        pickle.dump(Memo.memory, output)
        
    @staticmethod
    def a(self):
        print 'a'

if __name__ == '__main__':
    Memo.a(Memo)
    Memo.load()
    Memo.save()
    