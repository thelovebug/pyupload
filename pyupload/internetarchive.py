import json
import subprocess
import sys
import time

from ini import options


def upload_files(p_files):
    for (idx, l_file) in enumerate(p_files):
        l_derive = 0
        if idx + 1 == len(p_files):
            l_derive = 1

        print 'Uploading "%s" to archive.org, derivation : %d' % (l_file, l_derive)
        print
        l_proc = subprocess.Popen(
            ['curl', '--location', '--header', 'x-amz-auto-make-bucket:1',
             '--header',
             'authorization: LOW %s:%s' % (
                 options.internetarchive_access_key, options.internetarchive_secret_key),
             '--upload-file', l_file,
             '--header', 'x-archive-queue-derive:%d' % l_derive,
             'http://s3.us.archive.org/%s/%s/%s' % (
                 options.internetarchive_item, options.internetarchive_folder, l_file)],
            stdout=subprocess.PIPE)
        (l_out, _) = l_proc.communicate()
        print


def wait_for_derivation():
    print "Waiting for derivation to finish "
    l_reference_file = '/%s/%s_spectrogram.png' % (
        options.internetarchive_folder, options.auphonic_output_file_basename);

    while True:
        l_proc = subprocess.Popen(
            ['curl', '-s', '--location', '--header',
             'authorization: LOW %s:%s' % (
                 options.internetarchive_access_key, options.internetarchive_secret_key),
             'https://archive.org/details/%s&output=json' % options.internetarchive_item],
            stdout=subprocess.PIPE)
        (l_out, _) = l_proc.communicate()
        l_response = json.loads(l_out)
        for l_file in l_response['files']:
            if l_file == l_reference_file:
                print "Done"
                print
                return
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(15)


def list_urls():
    if not options.internetarchive_download:
        print "URLs of the uploaded files : "

    l_root = '/%s/%s' % (
        options.internetarchive_folder, options.auphonic_output_file_basename);
    l_proc = subprocess.Popen(
        ['curl', '-s', '--location', '--header',
         'authorization: LOW %s:%s' % (
             options.internetarchive_access_key, options.internetarchive_secret_key),
         'https://archive.org/details/%s&output=json' % options.internetarchive_item], stdout=subprocess.PIPE)
    (l_out, _) = l_proc.communicate()
    l_response = json.loads(l_out)
    for l_file in l_response['files']:
        if l_file.startswith(l_root):
            source_url = 'https://archive.org/download/%s%s' % (options.internetarchive_item, l_file)
            index = source_url.rfind('/')
            output_file = source_url[index + 1:]
            if options.internetarchive_download:
                print 'Downloading %s' % source_url
                proc = subprocess.Popen(["curl", "-L", source_url, "-o", output_file], stdout=subprocess.PIPE)
                proc.communicate()
            else:
                print source_url

    print

