import os
import os.path

if __name__ == '__main__':

    for dirpath, _, files in os.walk('.'):
        for file in files:
            if not file.endswith('.py'):
                continue

            module_path = os.path.join(dirpath, os.path.splitext(file)[0])[2:]
            module_name = '.'.join(module_path.split('/'))
            __import__(module_name)
