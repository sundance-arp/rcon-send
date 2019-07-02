#!/usr/bin/python3
import socket
import getpass
import random
import argparse


def init_args():
    parser = argparse.ArgumentParser(
            description='send command using rcon protocol'
            )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file')
    group.add_argument('--command')
    args = parser.parse_args()
    return args


def execute_command(sock, data_id, command):
    print("execute: " + command)
    payload = construct_execcommand(data_id, command)
    data = send_rcon(sock, payload)
    print_response(data)


def execute_command_file(sock, data_id, file_path):
    commands = ""
    with open(file_path, "r") as f:
        commands = f.readlines()

    for command in commands:
        execute_command(sock, data_id, command[:-1])


def construct_auth(data_id, data_password):
    payload = encode_payload(data_id, 3, data_password)
    return payload


def construct_execcommand(data_id, data_command):
    payload = encode_payload(data_id, 2, data_command)
    return payload


def encode_payload(data_id, data_type, data_body):
    data = b''
    data += data_id.to_bytes(4, 'little')
    data += data_type.to_bytes(4, 'little')
    data += data_body.encode('ascii') + b'\x00'

    payload = len(data).to_bytes(4, 'little') + data

    return payload


def send_rcon(sock, payload):
    sock.sendall(payload)

    data = sock.recv(4)
    size = int.from_bytes(data, 'little')
    data = sock.recv(size)

    return data


def is_authentication_success(data_id, data):
    auth_result = False
    if(int.from_bytes(data[0:4], 'little') == data_id):
        auth_result = True
    elif(data[0:4] == b'\xFF\xFF\xFF\xFF'):
        auth_result = False
    else:
        auth_result = False

    return auth_result


def print_response(data):
    print(data[8:].decode('ascii'))


def main():
    args = init_args()
    password = getpass.getpass()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('127.0.0.1', 25575))
        data_id = random.randint(0x00000000, 0xFFFFFFFE)
        data = None

        payload = construct_auth(data_id, password)
        data = send_rcon(sock, payload)
        if not is_authentication_success(data_id, data):
            print("Authentication failed.")
            exit(1)
        print("Authentication succeeded.")

        print('')

        if args.file is None:
            execute_command(sock, data_id, args.command)
        else:
            execute_command_file(sock, data_id, args.file)


if __name__ == '__main__':
    main()
