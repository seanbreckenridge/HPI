#!/usr/bin/env python3

"""
If last body weight entry was reported more than a week ago, returncode=1
Used in ./prompt_weight.job
"""

import sys

from datetime import datetime, timedelta

from my.body.weight import history

last_time: datetime = list(history())[-1].dt
now: datetime = datetime.utcnow()

# if its been more than 7 days
if now - last_time > timedelta(days=7):
    sys.exit(1)
