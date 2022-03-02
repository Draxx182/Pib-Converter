'''
By Draxx182
Credits go to Retraso for figuring out both Ishin pibs and Yakuza 0 pibs in the first place
Credits go to MinhGunKiss for helping me figure out how these pibs are formatted and testing the methods himself.
Credits go to Sutando for his PyBinaryReader
'''

#Imports
import math
import json
import sys
import os
import shutil
import time
from pathlib import Path
from collections import defaultdict
from binary_reader import BinaryReader

def BinaryCombine(read, write, type): #Takes the Reader Buffer and the Writer Buffer
    #Updates Writer by taking Reader output
    if (type == 4):
        output = read.read_uint32()
        write.write_uint32(output)
    elif (type == 2):
        output = read.read_uint16()
        write.write_uint16(output)
    elif (type == 1):
        output = read.read_uint8()
        write.write_uint8(output)
    elif (type == str):
        output = read.read_str(int(type))
        write.write_str(output)
    else:
        output = read.read_bytes(type)
        write.write_bytes(output)
    return output #Returns what the Reader had intially sent

if (len(sys.argv) <= 1):
    print('Drag and drop a Yakuza Ishin .pib file OR folder containing .pib files for the Pib Converter to work.')
    input("Press ENTER to exit... ")
else:
    propertyPath = sys.argv[1]
    if(propertyPath.endswith(".pib")):
        #//Read//
        wr = BinaryReader()
        wr.set_endian(True)
        with open(propertyPath, "rb") as f:
            rd = BinaryReader(f.read())
            rd.set_endian(True)

            #--File Header--
            fileInfo = BinaryCombine(rd, wr, 0x8)
            fileVersion = rd.read_uint32()
            if (fileVersion == 25):
                wr.write_uint32(27)
            fileFunny = BinaryCombine(rd, wr, 4)
            #--File Information--
            pibID = BinaryCombine(rd, wr, 4)
            numOfDDS = BinaryCombine(rd, wr, 4)
            BinaryCombine(rd, wr, 0x2A8)

            for DDS in range(numOfDDS):
                print("DDS #"+str(DDS+1)+" Done")
                #--DDS Info--
                BinaryCombine(rd, wr, 0x8)
                if (fileVersion == 25): #--Retraso: add group at 0x4 
                    wr.write_uint32(0)
                BinaryCombine(rd, wr, 0x78)
                if (fileVersion == 25): #Credit to Minh, this is what he saw on most working pibs.
                    wr.write_uint32(0xFFFFE334) #--Retraso: add 7 groups at 0x84
                    wr.write_uint32(0xFFFFECCD)
                    wr.write_uint32(0xFFFFE334)
                    wr.write_uint32(0xFFFFECCD)
                    wr.write_uint64(0)
                    wr.write_uint32(0)
                BinaryCombine(rd, wr, 0x114)
                #--DDS Data--
                DDSLength = 0
                DDSActual = BinaryCombine(rd, wr, 0x4)
                startOfDDS = rd.pos()
                for search in range(99999):
                    if (rd.pos() == rd.size()):
                        print("Check #1 | Reached End of File")
                        break
                    DDSCheck = rd.read_uint32()
                    if (DDSCheck == DDSActual):
                        rd.seek(rd.pos() - 408)
                        DDSBool = True
                        print("Check #2 | Reached New DDS File")
                        break
                endOfDDS = rd.pos()
                rd.seek(startOfDDS)
                DDSLength = (endOfDDS) - (startOfDDS)
                BinaryCombine(rd, wr, DDSLength)
        
        with open(propertyPath + " new.pib", "wb") as f:
            f.write(wr.buffer())