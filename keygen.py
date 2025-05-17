import random
import string
import json
import os
from app import get_novel_names


length = 32
characters = string.ascii_letters + string.digits + string.hexdigits

for novel in get_novel_names():
    key = ''
    for i in range(length):
        key += random.choice(characters)
        
    #print(key)

    # try to read existing data
    keys_data = {}
    if os.path.exists('keys.json'):
        with open('keys.json', 'r') as f:
            try:
                keys_data = json.load(f)
            except json.JSONDecodeError:
                keys_data = {}

    # write the updated data
    keys_data[novel] = key
    with open('keys.json', 'w') as f:
        json.dump(keys_data, f, indent=4)
        
print("Done.")