# -*- coding: utf8 -*-
import chardet

from kuankr_utils import log

def to_unicode(s, encoding='utf8'):
    if isinstance(s, str):
        s = s.decode(encoding)
    elif not isinstance(s, unicode):
        s = unicode(s)
    return s

def to_raw_str(s, encoding='utf8'):
    if isinstance(s, unicode):
        s = s.encode(encoding)
    return s

#try multi encoding list until success
def str_to_unicode(s, encoding=None):
    if s is None or encoding is None:
        return s

    if encoding == '__auto__':
        c = chardet.detect(s)
        log.debug("auto detected encoding: %s" % c)
        encoding = c['encoding']
        if encoding=='GB2312' or encoding=='GBK':
            #append GB18030 as alt
            #since many sites declares GB2312, but use GB18030 instead
            encoding = [encoding, 'GB18030']

    if not instance(encoding, list):
        encoding = [encoding]
    last_err = None
    for e in encoding:
        try:
            return s.decode(e)
        except UnicodeDecodeError, err:
            last_err = err
            continue
    raise last_err

def get_first_pinyin(t,codec="UTF8"):
    s = u'澳怖错堕贰咐过祸_骏阔络穆诺沤瀑群弱所唾__误迅孕座'
    if codec!="GBK":
        if not isinstance(t, unicode) and codec!="unicode":
            t=t.decode(codec)
        t=t.encode("GBK")
    if t<"\xb0\xa1" or t>"\xd7\xf9":
        return None
    for i in range(26):
        if s[i]!='_' and t<=s[i].encode("GBK"):
            return chr(ord('a')+i)
    return None

def get_first_pinyin_multiple(s, codec="UTF8"):
    from pinyin import pinyin
    if not isinstance(s, unicode) and codec!="unicode":
        s=s.decode(codec)
    return pinyin.str_to_initial_multi(s)

def strQ2B(ustring):
    """把字符串全角转半角"""
    ustring = to_unicode(ustring)
    rstring = u""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code==0x3000:
            inside_code=0x0020
        else:
            inside_code-=0xfee0
        if inside_code<0x0020 or inside_code>0x7e:      #转完之后不是半角字符则返回原来的字符
            rstring += uchar
        else:
            rstring += unichr(inside_code)
    return rstring

def strB2Q(ustring):
    """把字符串半角转全角"""
    ustring = to_unicode(ustring)
    rstring = u""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code<0x0020 or inside_code>0x7e:      #不是半角字符则返回原来的字符
            rstring += uchar
        else:
            if inside_code==0x0020: #除了空格其他的全角半角的公式为:半角=全角-0xfee0
                inside_code=0x3000
            else:
                inside_code+=0xfee0
            rstring += unichr(inside_code)
    return rstring


