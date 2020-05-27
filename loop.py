import os
import subprocess
import sys
import traceback

while True:
    try:
        if os.path.isfile('quit.txt'):
            os.remove('quit.txt')
            break
        p = subprocess.call([sys.executable, 'selfbot.py'])
    except:
        traceback.print_exc()
