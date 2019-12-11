#!/usr/bin/python3

import getpass
import os
import sys
import time
import socket
import traceback

import paramiko



def auth_setup(username, hostname):
    default_auth = 'p'
    auth = input("Authenticate by (p)assword or (r)sa key? [%s] " % default_auth)
    if len(auth) == 0:
        auth = default_auth

    if auth == 'r':
        default_path = os.path.join(os.environ["HOME"], ".ssh", "id_rsa")
        path = input("RSA key [%s]: " % default_path)
        if len(path) == 0:
            path = default_path
        try:
            key = paramiko.RSAKey.from_private_key_file(path)
        except paramiko.PasswordRequiredException:
            password = getpass.getpass("RSA key password: ")
            key = paramiko.RSAKey.from_private_key_file(path, password)
        t.auth_publickey(username, key)
    else:
        pw = getpass.getpass("Password for %s@%s: " % (username, hostname))
        t.auth_password(username, pw)

# logging
paramiko.util.log_to_file("python-ssh.log")

username = ''

if len(sys.argv) > 1:
    hostname = sys.argv[1]
    if hostname.find("@") >= 0:
        username, hostname = hostname.split("@")
else:
    hostname = input("Hostname: ")
if len(hostname) == 0:
    print(" !!! Please provide hostname !!! ")
    sys.exit(1)

port = 22

if hostname.find(":") >= 0:
    hostname, portstr = hostname.split(":")
    port = int(portstr)

# connect
try:
    client = SSHClient()
    client.load_system_host_keys(filename="~/.ssh/id_rsa")

# username
if username == '':
    default_username = getpass.getuser()
    username = input("Username [%s]: " % default_username)
    if len(username) == 0:
        username = default_username


