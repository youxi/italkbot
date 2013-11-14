#!/usr/bin/env python
# -*- coding:utf-8 -*- 


def is_chinese(uchar):
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False

def Q2B(uchar):
    inside_code=ord(uchar)
    if inside_code==0x3000:
        inside_code=0x0020
    else:
        inside_code-=0xfee0
    if inside_code<0x0020 or inside_code>0x7e:      
        return uchar
    return unichr(inside_code)
    

def stringQ2B(ustring):
    return "".join([Q2B(uchar) for uchar in ustring])
    

def uniform(ustring):
    return stringQ2B(ustring)


def getString(ustring):
    tar_string=''
    ustring=uniform(ustring)
    for uchar in ustring:
        if is_chinese(uchar):
            tar_string=tar_string+uchar+' '
        else:
            tar_string=tar_string+uchar

    return tar_string