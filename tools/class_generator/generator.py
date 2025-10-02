#generator.py
import os


DATA_TYPES = [
    "int",
    "string",
    "float",
    "byte"
]

# parse the file
def load_files(source_dir="messages") -> dict:
    retDict = {}
    try:
        files = os.listdir(source_dir)
        if len(files) > 0:
            for file in files:
                filename = source_dir + '/' + file
                fileObject = open(filename, 'r')
                retDict[file] = fileObject.readlines()
        return retDict
    except:
        print("error occurred in load_files()")

def dict_to_messages(dict):
    for key, value in dict.items():
        print(f"Processing {key}")
        value_as_str = process_file_data(value)

def process_file_data(tokens: list) -> str:
    
    tokens = list(map(lambda s: s.replace('\n', ''), tokens))

    tokens = "".join(tokens)
    
    if quick_syntax_check(tokens) is False:
        return None
    else:
        print('returned true')
        

def quick_syntax_check(text: str) -> bool:
    if check_braces(text) is False:
        return False

def check_braces(text):
    stack = []
    for char in text:
        if char == '{':
            stack.append('{')
        elif char == '}':
            if not stack:
                return False  # Too many closing braces
            stack.pop()
    return len(stack) == 0  # True if balanced


# driver code rn
raw_data_dict = load_files("messages")
dict_to_messages(raw_data_dict)