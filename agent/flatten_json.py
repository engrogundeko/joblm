from collections.abc import MutableMapping
crumbs = True
def flatten(dictionary, parent_key=False, separator='.'):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :return: A flattened dictionary
    """

    items = []
    for key, value in dictionary.items():
        if crumbs: print('checking:',key)
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            if crumbs: print(new_key,': dict found')
            if not value.items():
                if crumbs: print('Adding key-value pair:',new_key,None)
                items.append((new_key,None))
            else:
                items.extend(flatten(value, new_key, separator).items())
        elif isinstance(value, list):
            if crumbs: print(new_key,': list found')
            if len(value):
                for k, v in enumerate(value):
                    items.extend(flatten({str(k): v}, new_key, separator).items())
            else:
                if crumbs: print('Adding key-value pair:',new_key,None)
                items.append((new_key,None))
        else:
            if crumbs: print('Adding key-value pair:',new_key,value)
            items.append((new_key, value))
    return dict(items)

import json
with open(r"C:\Users\Admin\Desktop\SolveByte\jobLM\andrew_ng.json", "r") as file:
    file = json.load(file)
    flat_json = flatten(file)
    print(flat_json)
    
with open("flat_json.txt", "w") as file:
    file.write(str(flat_json))
