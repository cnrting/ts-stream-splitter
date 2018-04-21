# !usr/bin/env python
# coding:utf-8

from struct import unpack
import sys
import os
import getopt

psize = 188
chunksize = 8
sync_offset = -1
input_file = r"G:\input.ts"
filter_pid = (8191,)
output_location = "G:\\"
try:
    options, args = getopt.getopt(sys.argv[1:],"p:",["path="])
    for opt,arg in options:
        if opt in ("-p","--path"):
            output_location = arg
except getopt.GetoptError as e:
    print(e)
    sys.exit(0)

with open(input_file, 'rb') as ts:
    data = ts.read(1024)
    while 1:
        check_sync_offset = data.index(b'\x47')
        sync_offset += check_sync_offset + 1
        if data[check_sync_offset] == data[check_sync_offset+188]:
            break
        data = data[check_sync_offset+1:]
    sync_offset = sync_offset
    ts.seek(0)

    if sync_offset == -1:
        print('No sync bit in packet.')
        sys.exit(0)

    print("Sync_offset:",sync_offset)
    last_packet_length = (os.path.getsize(input_file)-sync_offset) % 188
    print("Last packet with length:", last_packet_length)

    output_file = output_location+input_file.split("\\")[-1]
    if os.path.exists(output_file):
        print("Output File Exist!")
        sys.exit(0)
    with open(output_file, 'wb') as t:
        if sync_offset != 0:
            t.write(ts.read(sync_offset))
        while True:
            data = ts.read(psize * chunksize)
            for i in range(chunksize):
                packet = data[:psize]
                data = data[psize:]
                if packet.__len__() == last_packet_length:
                    t.write(packet)
                    sys.exit(0)
                pid = unpack('>BHB184s', packet)[1] & 8191
                if(pid not in filter_pid):
                    t.write(packet)