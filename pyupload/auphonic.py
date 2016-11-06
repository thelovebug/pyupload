import json
import os.path
import subprocess
import sys
import time

from ini import config


def upload():
    print 'Uploading "%s" to Auphonic' % config.get('episode', 'file')
    print
    l_proc = subprocess.Popen(
        ['curl', '-X', 'POST', 'https://auphonic.com/api/simple/productions.json', '-u',
         '%s:%s' % (config.get('auphonic', 'username'), config.get('auphonic', 'password')), '-F',
         'preset=%s' % config.get('auphonic', 'preset'), '-F',
         'title=%s' % config.get('episode', 'title'), '-F', 'input_file=@%s' % config.get('episode', 'file'), '-F',
         'image=@%s' % config.get('episode', 'cover_art'), '-F', 'track=%s' % config.get('episode', 'number'), '-F',
         'output_basename=%s' % config.get('auphonic', 'output_file_basename'), '-F',
         'action=save'],
        stdout=subprocess.PIPE)
    (l_out, _) = l_proc.communicate()
    print
    return json.loads(l_out)


def start_production(p_uuid):
    print 'Starting auphonic production %s' % p_uuid
    l_proc = subprocess.Popen(
        ['curl', '-s', '-X', 'POST', 'https://auphonic.com/api/production/%s/start.json' % p_uuid,
         '-u', '%s:%s' % (config.get('auphonic', 'username'), config.get('auphonic', 'password'))],
        stdout=subprocess.PIPE)
    (l_out, _) = l_proc.communicate()
    print


def wait_for_production(uuid):
    print 'Waiting for production %s to be ready' % uuid
    while True:
        l_proc = subprocess.Popen(
            ['curl', '-s', '-X', 'GET', 'https://auphonic.com/api/production/%s.json' % uuid, '-u',
             '%s:%s' % (config.get('auphonic', 'username'), config.get('auphonic', 'password'))],
            stdout=subprocess.PIPE)
        (l_out, _) = l_proc.communicate()
        l_response = json.loads(l_out)
        l_status = l_response['data']['status']
        if l_status == 3:
            print "Done"
            print
            return
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(15)


def download_output_files(uuid):
    l_proc = subprocess.Popen(
        ['curl', '-s', '-X', 'GET', 'https://auphonic.com/api/production/%s.json' % uuid, '-u',
         '%s:%s' % (config.get('auphonic', 'username'), config.get('auphonic', 'password'))], stdout=subprocess.PIPE)
    (l_out, _) = l_proc.communicate()
    l_response = json.loads(l_out)
    l_downloaded_files = []
    for l_output_file in l_response['data']['output_files']:
        l_size = l_output_file['size']
        l_filename = l_output_file['filename']
        if os.path.isfile(l_filename) and os.path.getsize(l_filename) == l_size:
            print 'File %s already downloaded. Skipping.' % l_filename
            l_downloaded_files.append(l_filename)
            continue

        print 'Downloading "%s"' % l_output_file['filename']
        print
        proc = subprocess.Popen(
            ["curl", l_output_file['download_url'], "-u",
             "%s:%s" % (config.get('auphonic', 'username'), config.get('auphonic', 'password')), "-o", l_filename],
            stdout=subprocess.PIPE)
        proc.communicate()
        print
        l_downloaded_files.append(l_filename)

    return l_downloaded_files