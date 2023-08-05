# Amit Paz 319003455
# Yuval Alroy 315789461
import os
import socket
import sys
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from utils import push_data, pull_data, push_file, pull_file

flag = False


def create_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def create_folder():
    os.mkdir(os.path.abspath())


def connect_to_server(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    return s


def push_folder_to_server(sock, folder_path):
    with sock, sock.makefile('rb') as file:
        sock.sendall(b'add my folder\n')
        my_number = file.readline().strip().decode()
        my_id = file.readline().strip().decode()
        push_data(folder_path, sock)
        return my_id, my_number


def pull_folder_from_server(sock, my_path, folder_name):
    with sock, sock.makefile('rb') as file:
        sock.sendall(folder_name.encode() + b'\n')
        my_number = file.readline().strip().decode()
        pull_data(my_path, sock, file)
    return my_number


def create(src_path, file):
    new = file.readline().strip().decode()
    if new == 'new folder':
        try:
            os.makedirs(path + src_path)
        except:
            pass
    elif new == 'new file':
        pull_file(path + os.path.dirname(src_path), s, file)


def delete(src_path):
    for root, dirs, files in os.walk(src_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    if os.path.isdir(src_path):
        os.rmdir(src_path)
    elif os.path.isfile(src_path):
        os.remove(src_path)


def on_created(event):
    global flag
    if not flag:
        relative = str(event.src_path)[len(path):]
        with connect_to_server(ip_server, port_server) as sock:
            sock.sendall('created'.encode() + b'\n')
            sock.sendall(str(flag).encode() + b'\n')
            sock.sendall(client_number.encode() + b'\n')
            sock.sendall(relative.encode() + b'\n')
            if os.path.isdir(event.src_path):
                sock.sendall('new folder'.encode() + b'\n')
            else:
                sock.sendall('new file'.encode() + b'\n')
                push_file(event.src_path, sock)


def on_deleted(event):
    global flag
    if not flag:
        sock = connect_to_server(ip_server, port_server)
        relative = str(event.src_path)[len(path):]
        sock.sendall('deleted'.encode() + b'\n')
        sock.sendall(str(flag).encode() + b'\n')
        sock.sendall(client_number.encode() + b'\n')
        sock.sendall(relative.encode() + b'\n')


def on_moved(event):
    global flag
    if not flag:
        sock = connect_to_server(ip_server, port_server)
        relative_src = str(event.src_path)[len(path):]
        relative_dest = str(event.dest_path)[len(path):]
        sock.sendall('moved'.encode() + b'\n')
        sock.sendall(str(flag).encode() + b'\n')
        sock.sendall(client_number.encode() + b'\n')
        sock.sendall(relative_src.encode() + b'\n')
        sock.sendall(relative_dest.encode() + b'\n')
        if os.path.isdir(event.dest_path):
            sock.sendall('new folder'.encode() + b'\n')
        else:
            sock.sendall('new file'.encode() + b'\n')
            push_file(event.dest_path, sock)


def check_for_updates():
    sock = connect_to_server(ip_server, port_server)
    with sock, sock.makefile('rb') as file:
        sock.sendall('update me\n'.encode())
        sock.sendall(client_id.encode() + b'\n')
        sock.sendall(client_number.encode() + b'\n')
        length = int(file.readline().strip().decode())
        if length != -1:
            global flag
            flag = True
            for i in range(length):
                update_type = file.readline().strip().decode()
                update_src_path = file.readline().strip().decode()
                update_dst_path = file.readline().strip().decode()
                if update_type == 'created':
                    create(update_src_path, file)
                elif update_type == 'deleted':
                    delete(path + update_src_path)
                elif update_type == 'moved':
                    delete(path + update_src_path)
                    create(update_dst_path, file)
            flag = False


if __name__ == '__main__':
    ip_server = sys.argv[1]
    port_server = int(sys.argv[2])
    path = sys.argv[3]
    timer = int(sys.argv[4])
    s = connect_to_server(ip_server, port_server)
    if len(sys.argv) == 6:
        client_id = sys.argv[5]
        if not os.path.exists(path):
            os.mkdir(path)
        client_number = pull_folder_from_server(s, path, client_id)

    else:
        client_id, client_number = push_folder_to_server(s, path)
    s.close()

    # the file patterns we want to handle
    patterns = ["*"]
    # contains the patterns that we don’t want to handle
    ignore_patterns = None
    # boolean that we can set to True if we want to be notified just for regular files (not for directories)
    ignore_directories = False
    # boolean that if set to “True”, made the patterns we previously introduced “case sensitive”
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_moved = on_moved

    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    my_observer.start()
    try:
        while True:
            time.sleep(timer)
            check_for_updates()
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
