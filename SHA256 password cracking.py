from pwn import *
import sys

"""
This script performs a brute-force password hash cracking attempt using a wordlist.
It reads candidate passwords from `rockyou.txt`, computes their SHA-256 hash,
and compares each against a target hash provided as a command-line argument.

Modules:
- pwn: Provides logging and utility functions (e.g., sha256sumhex, log.progress).
- sys: Used to read command-line arguments.

Usage:
    python script.py <sha256sum>

Example:
    python script.py 5e884898da28047151d0e56f8dc62927...
"""

# === Argument Validation ===
if len(sys.argv) != 2:
    """
    Validates command-line arguments.
    Requires exactly one argument: the SHA-256 hash to crack.
    Prints usage instructions and exits if invalid.
    """
    print("invalid arguments!")
    print(">> {} <sha256sum>".format(sys.argv[0]))
    exit()

wanted_hash = sys.argv[1]
attempts = 0

# === Hash Cracking Loop ===
with log.progress("Attempting to back: {}!\n".format(wanted_hash)) as p:
    """
    Main brute-force loop:
    - Iterates through each password in rockyou.txt.
    - Computes its SHA-256 hash.
    - Compares against the target hash.
    - Tracks and logs the number of attempts.
    """

    with open("rockyou.txt", "r", encoding='latin-1') as password_list:
        for password in password_list:
            password = password.strip("\n").encode('latin-1')  # remove newline and encode
            password_hash = sha256sumhex(password)            # compute SHA-256 hash

            # Update progress bar with attempt details
            p.status("[{}] {} == {}".format(attempts, password.decode('latin-1'), password_hash))

            if password_hash == wanted_hash:
                """
                Success case:
                - If a password's hash matches the target, stop immediately.
                - Print success message with the discovered password.
                """
                p.success("Password hash found after {} attempts! {} hashes to {}!".format(
                    attempts, password.decode('latin-1'), password_hash))
                exit()

            attempts += 1

        """
        Failure case:
        If the end of the wordlist is reached without finding a match,
        notify the user that the password was not found.
        """
        p.failure("Password hash not found!")
