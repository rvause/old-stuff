#!/usr/bin/env python

import sys
import os
import subprocess
import simplejson

CONFIG_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'gomplayer_config.json')

def load_filetypes(definition_file):
    f = open(definition_file, 'r')
    json_string = f.read()
    f.close()
    return simplejson.loads(json_string)

def play_video(config):
    if len(sys.argv) < 2:
        print "Please supply video to play."
        return False
    video = sys.argv[1]
    try:
        filetype = sys.argv[2]
    except:
        filetype = os.path.splitext(video)[1][1:]
    print 'Playing: %s' % os.path.basename(video)
    print '**************************'
    
    if filetype in config:
        to_run = ['/usr/bin/mplayer',
            '-vo', config[filetype]['vo'],
            '-vc', config[filetype]['vc'],
            video
        ]
    else:
        to_run = ['/usr/bin/mplayer', video]
    
    result = subprocess.call(to_run)
    print '**************************'
    
    return result

print '******* GO!MPLAYER *******'  
conf = load_filetypes(CONFIG_FILE)
result = play_video(conf)

if result != 0 or result is False:
    print 'Something went wrong.'
else:
    print 'Hope you enjoyed your video!'
    
print '******* /GO!MPLAYER *******'
