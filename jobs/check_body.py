#!/usr/bin/env python3

"""
If last body weight entry was reported more than a week ago, returncode=1
Used in ./prompt_body.job
"""

import sys

from datetime import datetime, timedelta, timezone

from my.body import weight

last_logged_at = list(weight())[-1].when

# if its been more than 7 days since I logged my weight
if datetime.now(tz=timezone.utc) - last_logged_at > timedelta(days=7):
    sys.exit(1)
