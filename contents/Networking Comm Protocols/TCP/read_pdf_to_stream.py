import os
import hashlib
import queue
from queue import Queue
import random as rd
from datetime import datetime # use this lib to track the computation time.


'''
    This file is just going to read a PDF file and create a stream of bytes.
'''

# numbers_queue = queue.Queue()
numbers_queue = Queue()

def populate_queue(size=1000000):

    start = datetime.now()
    for i in range(0, size):
        numbers_queue.put(rd.randint(1, 100))
    stop = datetime.now()
    diff = (stop-start).total_seconds() 
    return diff

def printQueue():
    print(numbers_queue)

# def read_bytes_from_file(filename):
#     data = None
#     with open(filename, 'rb') as file:
#         data = file.readlines()
#         # for i in range(0,len(data)):
#         #     data[i] = data[i].rstrip()
#         #     print(data[i])
#         #     data[i] = data[i].decode('utf-8')
#         #     print(data[i])
#     print(data[1].rstrip().decode('cp1252'))
#     file.close()

# if 'lease_data.bin' in os.listdir('.'):
#     read_bytes_from_file('lease_data.bin')
# else:
#     print('error: not found')

def hash_file(filepath):
    # create a sha256 object
    sha256_hash = hashlib.sha256()

    print('calculating file size...')
    size_in_bytes = os.path.getsize(filepath)

    size_in_megabytes = size_in_bytes / (1024 * 1024)
    print('File size: {}'.format(size_in_megabytes))

    with open(filepath, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def encoding_experiment():
    original_text = 'hello, world, idk wtf is going to happen'

    encoded = original_text.encode('utf-8')
    print(encoded)

    # Convert each byte to its binary representation
    binary_string = ''.join(format(byte, '08b') for byte in encoded)

    print(binary_string)

def getFileSize(filepath) -> float:
    size_in_megabytes = os.path.getsize(filepath) / (1024 * 1024) # size in MB in one-line
    return size_in_megabytes

def compare_size(filepath, other_files_size) -> bool:
    fileA_size = getFileSize(filepath)

    if fileA_size == other_files_size:
        return True
    else:
        return False

time_diff = populate_queue()
printQueue()
print('total time spent init queue: {}'.format(time_diff))