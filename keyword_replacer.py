#!/bin/python3


import subprocess
import re


def VideoResolution( path ):
  """
  Returns the resolution of a file as detected by ffprobe
  """
  p = subprocess.Popen( ['ffprobe',path], stderr=subprocess.PIPE )

  output = p.stderr.read().decode()
  if 'Invalid data found' in output:
    return None

  # file all the occurances of two 3 digit numbers seperated by an 'x'
  reses = re.findall( '[0-9]{3,4}x[0-9]{3,4}', output )

  # split the resolution into y,x
  ret = reses[0].split('x')

  # make it x,y instead of y,x
  ret.reverse()

  return ret


def ReplaceKeyWords( new_file, file ):
  if '%res' in new_file:
    res = VideoResolution( file )
    res = 'x'.join(res)
    new_file = new_file.replace( '%res', res )

  return new_file

# command for title/artist
# ffprobe /data/music/Savior\ -\ Rise\ Against.mp3 2>&1| egrep "title\s+:\s+[a-zA-Z0-9 ]+"
