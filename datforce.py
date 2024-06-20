#!/usr/bin/python3
import getpass
import pexpect
import datetime
import time
import threading

def progress_bar(duration):
    total_time = duration  # Total time in seconds
    interval = 1  # Update interval for progress bar in seconds
    elapsed_time = 0

    while elapsed_time < total_time:
        # Calculate progress percentage
        progress = (elapsed_time / total_time) * 100
        progress = min(progress, 100)  # Ensure progress does not exceed 100%

        # Print the progress bar
        bar_length = 100
        filled_length = int(bar_length * progress / 100)
        bar = '=' * filled_length + ' ' * (bar_length - filled_length)
        print(f'\rWaiting: [{bar}] {elapsed_time}/{total_time}[s]', end='', flush=True)

        # Wait for the update interval
        time.sleep(interval)
        elapsed_time += interval

        if stop_event.is_set():
            exit()


hostname = input('Enter the hostname: ')
username = input('Enter username: ')
password = getpass.getpass('Enter password: ')

local_file_path = input('Enter local file path: ') #'/mnt/md0/qup/h5data'
remote_file_path = input('Enter remote file path: ') #'/group/cmb/kamioka/mKID/Ta-mKID/data/20240603_trigger_hdf5'

print(f'Synchronize data from {local_file_path} in your computer to {remote_file_path} at {hostname}')


def rsync_with_password(local_path, remote_path, password):
    # Construct the scp command
    command = f'rsync -avr --progress --partial {local_path} {remote_path}'
    print(command)
    # command = f"scp {local_path} {remote_path}"

    # Spawn the scp command
    child = pexpect.spawn(command, timeout=3600)

    try:
        # Define the expected prompt
        password_prompt = "password:"
        
        # Expect the password prompt and send the password
        child.expect(password_prompt)
        child.sendline(password)

        # Wait for the process to complete
        child.expect(pexpect.EOF)
        print(child.before.decode())

    except pexpect.exceptions.EOF as e:
        print(f"EOF encountered: {e}")
        print(f"rsync output: {child.before.decode()}")

    except pexpect.exceptions.TIMEOUT as e:
        print(f"Timeout waiting for rsync: {e}")
        print(f"rsync output: {child.before.decode()}")

    except Exception as e:
        print(f"Exception occurred: {e}")
        print(f"rsync output: {child.before.decode()}")

    finally:
        child.close()

def stop_button():
    while True:
        user_input = input("Enter 'stop' to stop: ")
        if user_input.lower() == "stop":
            stop_event.set()
            break
stop_event = threading.Event()
thread = threading.Thread(target=stop_button)
thread.daemon = True
thread.start()


def clear_screen():
    # ANSI escape sequence for clearing screen
    print('\033[H\033[J')


while not stop_event.is_set():
    #clear_screen()
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    #print('[Enter "stop" to kill')
    print(f'{now}: Synchronizing data from {local_file_path} to {remote_file_path}...')
    rsync_with_password(local_file_path, f'{username}@{hostname}:{remote_file_path}', password)
    #time.sleep(300)
    progress_bar(300)

