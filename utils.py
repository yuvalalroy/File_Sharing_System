import os

def pull_file(path, s, file):
    file_name = file.readline().strip().decode()
    file_size = int(file.readline().strip().decode())
    data = file.read(file_size)
    with open(os.path.join(path, file_name), 'wb') as f:
        f.write(data)


def push_file(path, s):
    with s:
        relative_file = os.path.basename(path)
        s.sendall(relative_file.encode() + b'\n')
        file_size = os.path.getsize(path)
        s.sendall(str(file_size).encode() + b'\n')
        with open(path, 'rb') as f:
            s.sendall(f.read())


def pull_data(path, s, file):
    number_files = int(file.readline().strip().decode())
    for i in range(number_files):
        file_name = file.readline().strip().decode()
        if file_name.endswith(',isdir'):
            name, isdir = file_name.split(',')
            new_path = create_inner_folder(name, path)
            pull_data(new_path, s, file)
        else:
            file_size = int(file.readline().strip().decode())
            data = file.read(file_size)
            with open(os.path.join(path, file_name), 'wb') as f:
                f.write(data)


def push_data(path, s):
    with s:
        files = os.listdir(path)
        s.sendall(str(len(files)).encode() + b'\n')
        for file in files:
            relative_file = os.path.join(path, file)
            if os.path.isdir(relative_file):
                s.sendall(file.encode() + b',isdir' + b'\n')
                push_data(relative_file, s)
            else:
                file_size = os.path.getsize(relative_file)
                s.sendall(file.encode() + b'\n')
                s.sendall(str(file_size).encode() + b'\n')
                with open(relative_file, 'rb') as f:
                    s.sendall(f.read())


def create_inner_folder(name, path):
    os.mkdir(os.path.join(path, name))
    return os.path.join(path, name)
