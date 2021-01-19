import time
import random
import threading

import requests

endpoints = ('1', '2', '3', '4', '')


def run():
    while True:
        try:
            target = random.choice(endpoints)
            requests.get("http://nginx:4000/users/%s" % target, timeout=1)
        except:
            pass


if __name__ == '__main__':
    for _ in range(4):
        thread = threading.Thread(target=run)
        thread.setDaemon(True)
        thread.start()

    while True:
        time.sleep(1)
