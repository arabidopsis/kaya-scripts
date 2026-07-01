# /// script
# requires-python = ">=3.10"
# ///

import sys
import secrets

# uv run chpasswd.py /mnt/s-ws/s-* > passwords
# sudo chpasswd < passwords
d = {}
for home in sys.argv[1:]:
    # expecting /mnt/s-ws/s-nnn
    user = home.split("/")[-1]
    d[user] = secrets.token_urlsafe(6)
for user, pw in sorted(d.items()):
    print(f"{user}:{pw}")
