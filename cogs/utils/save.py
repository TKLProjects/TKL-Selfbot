import asyncio
import json
import logging
import os
import sys

log = logging.getLogger('LOG')
loop = asyncio.get_event_loop()
lock = asyncio.Lock()


def read_json(file_name):
    with open('config/' + file_name + '.json', 'r') as f:
        try:
            cont = json.load(f)
            return cont
        except:
            return None


def reading_key(file_name, searched):
    with open('config/' + file_name + '.json', 'r') as f:
        cont = json.load(f)
        try:
            return cont[searched]
        except:
            return None


def read_config(searched):
    return reading_key("config", searched)


def read_log(searched):
    return reading_key("log", searched)


def saving(file_name, field, value):
    with open('config/' + file_name + '.json', 'r') as q:
        content = json.load(q)
        secure_content = content
        with open('config/' + file_name + '.json', 'w') as f:
            try:
                content[field] = value
                f.seek(0)
                f.truncate()
                json.dump(content, f, indent=4, separators=(',', ':'))
                return True
            except Exception as e:
                f.seek(0)
                f.truncate()
                json.dump(secure_content, f, indent=4, separators=(',', ':'))
                log.error("An Error occurd while saving")
                return e


async def save_config(field, value):
    with await lock:
        return await loop.run_in_executor(None, saving, 'config', field, value)


async def save_log(field, value):
    with await lock:
        return await loop.run_in_executor(None, saving, 'log', field, value)


async def save_commands(field, value):
    with await lock:
        return await loop.run_in_executor(None, saving, 'commands', field, value)


def deleting_key(file_name, key):
    with open('config/' + file_name + '.json', 'r') as q:
        content = json.load(q)
        secure_content = content
        with open('config/' + file_name + '.json', 'w') as f:
            try:
                del content[key]
                f.seek(0)
                f.truncate()
                json.dump(content, f, indent=4, separators=(',', ':'))
                return True
            except Exception as e:
                f.seek(0)
                f.truncate()
                json.dump(secure_content, f, indent=4, separators=(',', ':'))
                log.error("An Error occurd while saving")
                return e


async def delete_key(file_name, key):
    with await lock:
        return await loop.run_in_executor(None, deleting_key, file_name, key)


def check_existence(filename):
    if not os.path.isfile('config/' + filename + '.json'):
        if os.path.isfile('config/' + filename + '.json.example'):
            os.rename('config/' + filename + '.json.example', 'config/' + filename + '.json')
            log.warning(f"Renamed {filename}.json.example to {filename}.json, you should go end check that everything is set up correctly")
        else:
            log.error(f"File {filename} is missing, shutting down the bot.")
            python = sys.executable
            os.execl(python, python, *sys.argv)
