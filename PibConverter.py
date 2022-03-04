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

def IshinWrite(ishin_path):
    wr = BinaryReader()
    wr.set_endian(True)
    #//Read//
    with open(ishin_path, "rb") as f:
        rd = BinaryReader(f.read())
        rd.set_endian(True)

        #--File Header--
        fileInfo = BinaryCombine(rd, wr, 0x8)
        fileVersion = rd.read_uint32()
        if (fileVersion == 25):
            wr.write_uint32(27)
        else:
            return str(ishin_path)+" not converted! (Pib not correct version)"
        fileFunny = BinaryCombine(rd, wr, 4)
        #--File Information--
        pibID = BinaryCombine(rd, wr, 4)
        numOfDDS = BinaryCombine(rd, wr, 4)
        BinaryCombine(rd, wr, 0x2A8)

        for DDS in range(numOfDDS):
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
                if (rd.pos() == rd.size()): #Reaches end of file
                    break
                DDSCheck = rd.read_uint32()
                if (DDSCheck == DDSActual): #Reaches another DDS node
                    rd.seek(rd.pos() - 408)
                    DDSBool = True
                    break
            endOfDDS = rd.pos()
            rd.seek(startOfDDS)
            DDSLength = (endOfDDS) - (startOfDDS)
            BinaryCombine(rd, wr, DDSLength)
    
    #//Write//
    with open(ishin_path, "wb") as f:
        f.write(wr.buffer())
    return ishin_path + " converted!"

if (len(sys.argv) <= 1):
    print('Drag and drop a Yakuza Ishin .pib file OR folder containing .pib files for the Pib Converter to work.')
    input("Press ENTER to exit... ")
else:
    numOfFiles = 0
    propertyPath = sys.argv[1]
    if(propertyPath.endswith(".pib")):
        print(IshinWrite(propertyPath))
    elif(os.path.isdir(propertyPath)):
        for path, dirs, files in os.walk(propertyPath):
            for f in files:
                file_path = os.path.join(path, f)
                if file_path.endswith(".pib"):
                    print(IshinWrite(file_path))
    else:
        print("Bad filetype.")
