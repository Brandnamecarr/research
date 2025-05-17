import os

def readFile(filename):
    data = None
    
    with open(filename, 'r') as f:
        data = f.readlines()
        print(process(data))

def parse_messages(data):
    classes = {}
    current_class = None
    variables = []

    for line in data:
        line = line.strip()
        if line.startswith('message '):
            current_class = line.split()[1]
            variables = []
        elif line == '}':
            if current_class:
                classes[current_class] = variables
            current_class = None
        elif current_class and line:
            parts = line.split()
            if len(parts) == 2:
                var_type, var_name = parts
                variables.append((var_type, var_name))

    class_defs = []
    for class_name, vars in classes.items():
        class_str = f"class {class_name.capitalize()}:\n"
        # Constructor
        class_str += "    def __init__(self"
        for var_type, var_name in vars:
            py_type = type_map.get(var_type, var_type)
            class_str += f", {var_name}: {py_type}"
        class_str += "):\n"
        for _, var_name in vars:
            class_str += f"        self._{var_name} = {var_name}\n"
        class_str += "\n"

        # Getters and Setters
        for _, var_name in vars:
            class_str += f"    def get_{var_name}(self):\n"
            class_str += f"        return self._{var_name}\n\n"
            class_str += f"    def set_{var_name}(self, value):\n"
            class_str += f"        self._{var_name} = value\n\n"

        class_defs.append(class_str.strip())

    return "\n\n".join(class_defs)

        

if __name__ == '__main__':

    filename = "messages/temp.msg"
    readFile(filename)