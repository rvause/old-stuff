from randomplaylist.generator import PlaylistGenerator

generator = PlaylistGenerator()

files = generator.make_list()
generator.save_list('xspf')
generator.save_list('pls')
generator.save_list('m3u')

#for f in files:
#    print f
