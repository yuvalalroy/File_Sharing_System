# Amit Paz 319003455
# Yuval Alroy 315789461
import os
import random
import socket
import string
import sys

from utils import push_data, pull_data, pull_file, push_file

max_port = 65535
min_port = 1023

clients_dic = {}


def add_to_dic(client_id, num):
    if client_id not in clients_dic:
        clients_dic[client_id] = {num: []}
    elif num not in clients_dic[client_id]:
        clients_dic[client_id][num] = []


def insert_updates(client_id, num, src_path, event, dst_path):
    for key in list(clients_dic[client_id].keys()):
        if str(key) != str(num):
            if dst_path == '':
                clients_dic[client_id][key].append([event, src_path])
            else:
                clients_dic[client_id][key].append([event, src_path, dst_path])


def delete_path(src_path):
    for root, dirs, files in os.walk(src_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    if os.path.isdir(src_path):
        os.rmdir(src_path)
    else:
        try:
            os.remove(src_path)
        except:
            pass


def delete_updates(client_id, num, event, src_path, dst_path):
    updates_list = clients_dic[client_id][num]
    if dst_path == '':
        wanted_update = [event, src_path]
    else:
        wanted_update = [event, src_path, dst_path]
    for update in updates_list:
        if update == wanted_update:
            clients_dic[client_id][num].remove(wanted_update)


def init_clients_folder():
    os.mkdir(os.path.abspath('Clients'))
    return os.path.abspath('Clients')


def create_new_client_id(num):
    client_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(128))
    os.mkdir(os.path.join(os.path.abspath('Clients'), client_id))
    print(client_id)
    add_to_dic(client_id, num)
    return client_id


def create_socket(path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', PORT))
    s.listen()
    while True:
        client_socket, client_address = s.accept()
        with client_socket, client_socket.makefile('rb') as file:
            data = file.readline().strip().decode()

            if data == 'add my folder':
                num = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(128))
                client_socket.sendall(num.encode() + b'\n')
                client_id = create_new_client_id(num)
                client_socket.sendall(client_id.encode() + b'\n')
                folder_path = path + '/' + str(client_id)
                pull_data(folder_path, client_socket, file)

            elif data == 'update me':
                client_id = file.readline().strip().decode()
                client_number = file.readline().strip().decode()
                length = len(clients_dic[client_id][client_number])
                if length == 0:
                    client_socket.sendall(str(-1).encode() + b'\n')
                    client_socket.close()
                    continue
                client_socket.sendall((str(length)).encode() + b'\n')
                temp_list = clients_dic[client_id][client_number]
                for i in range(0, length):
                    event = temp_list[i][0]
                    client_socket.sendall(event.encode() + b'\n')
                    src_path = temp_list[i][1]
                    client_socket.sendall(src_path.encode() + b'\n')
                    if len(temp_list[i]) == 2:
                        dst_path = ''
                    else:
                        dst_path = temp_list[i][2]
                    client_socket.sendall(dst_path.encode() + b'\n')
                    if event == 'created':
                        full_path = str(os.path.abspath('Clients') + '/' + str(client_id) + src_path)
                        if os.path.isdir(full_path):
                            client_socket.sendall('new folder'.encode() + b'\n')
                        else:
                            client_socket.sendall('new file'.encode() + b'\n')
                            push_file(full_path, client_socket)

                    if event == 'moved':
                        full_path = str(os.path.abspath('Clients') + '/' + str(client_id) + dst_path)
                        if os.path.isdir(full_path):
                            client_socket.sendall('new folder'.encode() + b'\n')
                        else:
                            client_socket.sendall('new file'.encode() + b'\n')
                            push_file(full_path, client_socket)

                clients_dic[client_id][client_number].clear()
                temp_list.clear()

            elif data == 'created':
                flag = file.readline().strip().decode()
                if flag == 'False':
                    client_number = file.readline().strip().decode()
                    relative_path = file.readline().strip().decode()
                    new = file.readline().strip().decode()
                    if new == 'new folder':
                        try:
                            os.makedirs(os.path.abspath('Clients') + '/' + str(client_id) + relative_path)
                        except:
                            pass
                    elif new == 'new file':
                        pull_file(os.path.abspath('Clients') + '/' + str(client_id) + os.path.dirname(relative_path),
                                  client_socket, file)

                    insert_updates(client_id, client_number, relative_path, data, '')

            elif data == 'deleted':
                flag = file.readline().strip().decode()
                if flag == 'False':
                    client_number = file.readline().strip().decode()
                    src_path = file.readline().strip().decode()
                    insert_updates(client_id, client_number, src_path, data, '')
                    delete_path(os.path.abspath('Clients') + '/' + str(client_id) + src_path)

            elif data == 'moved':
                flag = file.readline().strip().decode()
                if flag == 'False':
                    client_number = file.readline().strip().decode()
                    src_path = file.readline().strip().decode()
                    relative_path = file.readline().strip().decode()
                    insert_updates(client_id, client_number, src_path, data, relative_path)
                    delete_path(os.path.abspath('Clients') + '/' + str(client_id) + src_path)
                    new = file.readline().strip().decode()
                    if new == 'new folder':
                        try:
                            os.makedirs(os.path.abspath('Clients') + '/' + str(client_id) + relative_path)
                        except:
                            pass
                    elif new == 'new file':
                        pull_file(os.path.abspath('Clients') + '/' + str(client_id) + os.path.dirname(relative_path),
                                  client_socket, file)

            else:
                num = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(128))
                add_to_dic(client_id, num)
                client_socket.sendall(num.encode() + b'\n')
                push_data(os.path.abspath('Clients') + '/' + data, client_socket)

        client_socket.close()


# check if port is valid
def check_port(port):
    if not min_port <= port <= max_port:
        sys.exit()


# main method
if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit()
    try:
        PORT = int(sys.argv[1])
        check_port(PORT)
        path = init_clients_folder()
        create_socket(path)
    except ValueError:
        sys.exit()
