#-d
# only print what would be done; don"t actually rename anything

#-f 'dexter episode.*'
# only work with files that match this regex. mostly just a shortcut so you can
# just pass in all the files in the current directory instead of trying to
# pick and choose with bash.

#-r 'Dexter E[0-9]\.mp4\'
# never rename to something that doesn't match this. this is used to
# ensure that something can't be renamed to something you aren't expecting.

#-a 'r:dexter episode ([0-9]).*\.mp4:Dexter E\1.mp4'
# r:one:two
# replace occurances of one with two in all file names

python rename.py -d -f 'example/dexter episode.*' -r 'example/Dexter E[0-9]\.mp4' -a 'r:dexter episode ([0-9]).*\.mp4:Dexter E\1.mp4' example/*