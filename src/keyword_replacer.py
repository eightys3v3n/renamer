#!/bin/python3


import subprocess
import unittest
import re
import os
from collections import defaultdict


def VideoResolution( path ):
  """ Returns the resolution of a file, 'XxY', as detected by ffprobe
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
  ret = 'x'.join(ret)

  return ret


def SongTitle( path ):
  """ Returns the title of a music file as detected by ffprobe
  """
  p = subprocess.Popen( ['ffprobe',path], stderr=subprocess.PIPE )

  output = p.communicate()[1].decode()
  if 'Invalid data found' in output:
    return None

  # find the first occurance of "title : stuff" with any number of spaces.
  res = re.search( r'title\s+:\s+([a-zA-Z0-9,\(\) ]+)', output )

  if res is None:
    return ""

  ret = res.group(1)

  return ret


KEYWORD_PREFIX = '%'
KEYWORDS = {
  'res': VideoResolution,
  'title': SongTitle,
}


def ReplaceKeyWords( new_file, file ):
  for keyword, func in KEYWORDS.items():
    trigger_word = f'{KEYWORD_PREFIX}{keyword}'
    if trigger_word in new_file:
      res = func( file )
      new_file = new_file.replace( trigger_word, res)

  return new_file


class Test(unittest.TestCase):
  SONG_TITLE_FILE = "tests/test_song.mp3"

  @classmethod
  def setUpClass(cls):
    if not os.path.exists(cls.SONG_TITLE_FILE):
      raise Exception(f"Missing test file '{cls.SONG_TITLE_FILE}'")

  def test_song_title(self):
    res = SongTitle(self.SONG_TITLE_FILE)
    self.assertEqual("Example Title", res)
