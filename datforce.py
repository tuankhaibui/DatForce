#!/usr/bin/python3

import getpass
import pexpect
import datetime
import time
import threading
import keyboard

hostname = input('Enter the hostname: ')
username = getpass.getpass('Enter username: ')
password = getpass.getpass('Enter password: ')

local_file_path = input('Enter local file path: ') #'/mnt/md0/qup/h5data'
remote_file_path = input('Enter remote file path: ') #'/group/cmb/kamioka/mKID/Ta-mKID/data/20240603_trigger_hdf5'

print(f'Synchronize data from {local_file_path} in your computer to {remote_file_path} at {hostname}')

# cmd = f"rsync -avz --delete -e ssh {local_file_path} {username}@{hostname}{remote_file_path}"


def rsync_with_password(local_path, remote_path, password):
    # Construct the scp command
    command = f'rsync -avz -e ssh {local_path} {remote_path}'
    print(command)
    # command = f"scp {local_path} {remote_path}"

    # Spawn the scp command
    child = pexpect.spawn(command)

    # Define the expected prompt
    password_prompt = "password:"

    # Expect the password prompt and send the password
    child.expect(password_prompt)
    child.sendline(password)

    # Wait for the process to complete
    child.expect(pexpect.EOF)
    print(child.before.decode())

stop_event = threading.Event()

def stop_button():
    while True:
        user_input = input("Enter 'stop' to stop: ")
        if user_input.lower() == "stop":
            stop_event.set()
            break

thread = threading.Thread(target=stop_button)
thread.daemon = True
thread.start()

# while True:
while not stop_event.is_set():
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f'{now}: Synchronizing data from {local_file_path} to {remote_file_path}...')
    rsync_with_password(local_file_path, f'{username}@{hostname}:{remote_file_path}', password)
    time.sleep(1)
