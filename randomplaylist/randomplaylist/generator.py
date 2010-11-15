import os
import random
import json
import subprocess


class PlaylistGenerator():
    
    def __init__(self, *args, **kwargs):
        self.home_dir = kwargs.get('home_dir', os.path.expanduser('~'))
        self.media_path = kwargs.get('media_path', os.path.join(self.home_dir, 'media'))
        self.control_file = kwargs.get('control_file', 'control.json')
        self.allowed_extensions = kwargs.get('allowed_extensions', ('.mp4', '.mkv', '.mov'))
        self.control_path = os.path.join(self.media_path, self.control_file)
        self.doubles_passes = kwargs.get('doubles_passes' , 10)
        self.playlist_dir = kwargs.get('playlist_dir', os.path.join(self.home_dir, 'playlists'))
        self.files = []
        self.basefiles = []
        self.control = {}
        
    def scan_for_media(self):
        for root, dirs, items in os.walk(self.media_path):
            for item in items:
                basename, ext = os.path.splitext(item)
                if ext in self.allowed_extensions:
                    self.files.append(os.path.join(root, item))
        self.basefiles = [ (os.path.basename(f).strip(), f) \
                           for f in self.files ]

    def get_control(self):
        if os.path.isfile(self.control_path):
            f = open(self.control_path, 'r')
            json_string = f.read()
            f.close()
            self.control = json.loads(json_string)

    def apply_control(self):
        for base, filepath in self.basefiles:
            if base in self.control:
                if 'options' in self.control[base]:
                    if 'plays_in_loop' in self.control[base]['options']:
                        if self.control[base]['options']['plays_in_loop'] > 0:
                            for i in range(self.control[base]['options']['plays_in_loop']-1):
                                self.files.append(filepath)

    def check_doubles(self, *args, **kwargs):
        """
        Checks for concurrent entries to save the playlist from playing the same
        video twice in succession.
        
        You can make more than default passes by passing passes kwarg.
        """
        max_passes = kwargs.get('passes', self.doubles_passes)
        last = ''
        double = True
        passes = 0
        while double and passes <= max_passes:
            double = False
            for f in self.files:
                if f == last:
                    random.shuffle(self.files)
                    double = True
                last = f
            passes = passes + 1
            
    def make_list(self):
        self.scan_for_media()
        self.get_control()
        self.apply_control()
        self.check_doubles()
        return self.files
    
    def get_info(self, basename, item):
        if basename in self.control:
            title = self.control[basename].get('title', 'No Title')
            duration = self.control[basename].get('duration', self.get_duration(item))
        else:
            duration = self.get_duration(item)
            title = 'No Title'
            
        return (title, duration)
    
    def write_m3u(self):
        try:
            f = open(os.path.join(self.playlist_dir, 'playlist-1.m3u'), 'w')
        except:
            print 'Error: can not write to file.'
            
        f.write('#EXTM3U\n')
            
        for item in self.files:
            basename = os.path.basename(item)
            if basename in self.control:
                title = self.control[basename].get('title', 'No Title')
                duration = self.control[basename].get('duration', self.get_duration(item))
            else:
                duration = self.get_duration(item)
                title = 'No Title'
            f.write('#EXTINF:%s,%s\n%s\n' % (duration, title, item))
        
        f.close()
        
    def write_pls(self):
        try:
            f = open(os.path.join(self.playlist_dir, 'playlist-1.pls'), 'w')
        except:
            print 'Error: can not write to file.'
            
        f.write('[playlist]\n')
        x = 0
        for item in self.files:
            x += 1
            title, duration = self.get_info(os.path.basename(item), item)
            f.write('File%s=%s\n' % (x, item))
            f.write('Title%s=%s\n' % (x, title))
            f.write('Length%s=%s\n' % (x, duration))
        
        f.write('NumberOfEntries=%s\n' % x)
        f.write('Version=2\n')
        f.close()        
        
    def write_xspf(self):
        try:
            f = open(os.path.join(self.playlist_dir, 'playlist-1.xspf'), 'w')
        except:
            print 'Error: can not write to file.'
            
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<playlist version="1" xmlns="http://xspf.org/ns/0/">\n')
        f.write('\t<trackList>\n')
        
        for item in self.files:
            title, duration = self.get_info(os.path.basename(item), item)            
            duration = int(duration) * 1000
            f.write('\t\t<track>\n')
            f.write('\t\t\t<location>file://%s</location>\n' % item)
            f.write('\t\t\t<title>%s</title>\n' % title)
            f.write('\t\t\t<duration>%s</duration>\n' % duration)
            f.write('\t\t</track>\n')
        
        f.write('\t</trackList>\n')
        f.write('</playlist>')
        
        f.close()
    
    def save_list(self, playlist_format):
        if not os.path.isdir(self.playlist_dir):
            try:
                os.mkdir(self.playlist_dir)
            except:
                print 'Error: Failed to create playlist directory.'
                return False
            
        if playlist_format == 'm3u':
            self.write_m3u()
        if playlist_format == 'xspf':
            self.write_xspf()
        if playlist_format == 'pls':
            self.write_pls()
        
    def get_duration(self, filename):
        result = subprocess.Popen(['/usr/share/mplayer/midentify.sh', filename],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in result.stdout.readlines():
            if 'ID_LENGTH' in line:
                exec(line)
        return str(int(round(ID_LENGTH)))
