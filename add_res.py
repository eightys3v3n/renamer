#!/bin/python3

from getopt import getopt
import subprocess
import shutil
import sys
import os
import re


# this is a test change


def Resolution( path ):
  p = subprocess.Popen( ['ffprobe',path], stderr=subprocess.PIPE )
  output = p.stderr.read().decode()
  if 'Invalid data found' in output:
    return None

  reses = re.findall( '[0-9]{3,4}x[0-9]{3,4}', output )
  return reses[0]


def main():
  opts, args = getopt( sys.argv[1:], 'pr', [ 'print', 'rename' ] )
  files = []
  resolution = False
  rename = False

  for opt, arg in opts:
    if opt in [ '-p', '--print' ]:
      resolution = True
    elif opt in [ '-r', '--rename' ]:
      rename = True

  print( 'obtaining files' )
  for arg in args:
    if os.path.exists( arg ):
      ext  = arg[ arg.rfind('.')+1: ]
      name = arg[ 0: arg.rfind('.') ]
      res = Resolution( arg )
      if res is not None:
        files.append( {
          'name':name,
          'res':res,
          'ext':ext
        } )

  for file in files:
    r = file['res']
    n = file['name']
    e = file['ext']
    old = n+'.'+e
    new = n+' ('+r+').'+e

    if resolution:
      print( r+"|"+old )

    elif rename:
      if r in n:
        continue

      choice = input( old+' -> '+new+' ' )
      if choice in [ 'yes', 'y', 'YES', 'Y' ]:
        if os.path.exists( new ):
          choice = input( 'overwrite ' )
          if choice not in [ 'yes', 'y', 'YES', 'Y' ]:
            print( "skipped" )
            continue
        shutil.move( old, new )

      else:
        print( "skipped" )


if __name__ == '__main__':
  main()