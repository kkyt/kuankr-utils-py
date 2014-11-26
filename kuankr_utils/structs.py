import struct
import six

from kuankr_utils import date_time

def unpack (format, buffer) :
    #TODO speed up

    targs = []
    if format.find('t') >= 0 or format.find('T') >= 0:
        arg_number = 0
        new_format = ''
        for c in format:
            if c == 't' or c == 'T':
                #datetime
                targs.append((arg_number, c))
                new_format += 'Q'
                arg_number += 1
            else:
                new_format += c
                if c in 'cbB?hHiIlLqQfdspPzZ' :
                    arg_number += 1
        format = new_format

    while True:
        pos = format.find ('z')
        if pos>=0:
            asciiz_start = struct.calcsize(format[:pos])
            asciiz_len = buffer[asciiz_start:].find('\0')
            format = '%s%dsx%s' % (format[:pos], asciiz_len, format[pos+1:])
        else:
            break

    #can only support one Z
    pos = format.find ('Z')
    if pos>=0:
        start = struct.calcsize (format[:pos])
        end = struct.calcsize (format[pos+1:])
        asciiz_len = len(buffer)-start-end
        if asciiz_len<0:
            raise Exception("invalid format: %s for buffer: [%s]" % (format, buffer))
        format = '%s%ds%s' % (format[:pos], asciiz_len, format[pos+1:])

    r = struct.unpack(format, buffer)
    if targs:
        r = list(r)
        for t,c in targs:
            if c=='t':
                r[t] = date_time.from_microsecond(r[t])
            else:
                x = date_time.from_microsecond_ad(r[t])
                #TODO: convert to string?
                r[t] = date_time.to_str(x)
        r = tuple(r)
    return r

def pack(format, *args):
    if not format:
        return ''
    new_format = ''
    arg_number = 0
    new_args = list(args)
    for c in format :
        a = args[arg_number]
        if c == 'z' or c == 'Z':
            if isinstance(a, unicode):
                a = a.encode('utf8')
                new_args[arg_number] = a
            n = len(a)
            if c=='z':
                n += 1
            new_format += '%ds' % n
            arg_number += 1
        elif c == 't' or c == 'T':
            #datetime
            if a is None:
                #convert datetime==None to 0
                a = 0
            elif not isinstance(a, six.integer_types):
                if c == 't':
                    a = date_time.to_microsecond(a)
                elif c == 'T':
                    a = date_time.to_microsecond_ad(a)

            #NOTE: force converting to >=0
            if a<0:
                a = 0

            new_args[arg_number] = a
            new_format += 'Q'
            arg_number += 1
        else :
            new_format += c
            if c in 'cbB?hHiIlLqQfdspP' :
                arg_number += 1
    return struct.pack(new_format, *new_args)


