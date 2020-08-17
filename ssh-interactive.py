import getpass
import os
import sys
import time
import socket
import traceback

import paramiko

import Interactive
from . import Interactive

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
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname,port))
except Exception as e:
    print(" !!! Connection Failed: " + str(e))
    traceback.print_exc()
    sys.exit(1)

try:
    t = paramiko.Transport(sock)
    try:
        t.start_client()
    except paramiko.SSHException:
        print(" !!! SSH negotiation failed !!!")
        sys.exit(1)

    try:
        keys = paramiko.util.load_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
    except IOError:
        try:
            keys = paramiko.util.load_host_keys(os.path.expanduser("~/ssh/known_hosts"))
        except IOError:
            print(" !!! Unable to open host keys file !!! ")
            keys = {}

    # check host key on remote server
    key = t.get_remote_server_key()
    if hostname not in keys:
        print(" !!! WARNING: unknown host key !!! ")
    elif key.get_name() not in keys[hostname]:
        print(" !!! WARNING: host key has changed !!! ")
        print(key.get_name())
        print(keys[hostname])
        sys.exit(1)
    else:
        print(" *** host key OK *** ")

    # username
    if username == '':
        default_username = getpass.getuser()
        username = input("Username [%s]: " % default_username)
        if len(username) == 0:
            username = default_username

    auth_setup(username, hostname)
    if not t.is_authenticated():
        print(" !!! Authentication failed !!! ")
        t.close()
        sys.exit(1)

    chan = t.open_session()
    chan.get_pty()
    chan.invoke_shell()
    print(" *** starting shell... *** \n")
    Interactive.interactive_shell(chan)
    chan.close()
    t.close()

except Exception as e:
    print(" !!! caught exception: " + str(e.__class__) + ": " + str(e))
    traceback.print_exc()
    try:
        t.close()
    except:
        pass
    sys.exit(1)

