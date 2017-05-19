#!/bin/python3

from getopt import getopt
import unittest
import textwrap
import shutil
import sys
import os
import re


global verbose, true, false
true  = True
false = False
verbose = false


def GetFiles( args, filter_re=None ):
  global verbose
  files = []
  Matches = None

  if filter_re is not None:
    filter = filter_re
    def Matches( pattern, source ):
      if re.match( pattern, source ):
        return True
      else:
        return False

  else:
    def Matches( pattern, source ):
      return True


  for arg in args:
    if os.path.isfile( arg ):
      if Matches( filter_re, arg ):
        files.append( arg )
      elif verbose:
        print( "file doesn't match filter '{}'".format( arg ) )
    elif verbose:
      print( "file doesn't exist '{}'".format( arg ) )

  return files


def ParseAction( raw ):
  action = [ '' ]

  if raw[0:2] == 'd:':
    action[0] = 'remove'
    raw = raw[2:]

    action.append( raw )

  elif raw[0:2] == 'r:':
    action[0] = 'replace'
    raw = raw[2:]

    res = re.split( '(?<!\\\):', raw )
    res[0] = res[0].replace( '\\:', ':' )
    res[1] = res[1].replace( '\\:', ':' )
    action.extend( res )

  else:
    raise Exception( "invalid action", raw[0:2] )

  return tuple( action )


def DoAction( action, file ):
  new_file = None

  if action[0] == 'remove':
    new_file = re.sub( action[1], '', file )
    if new_file == file:
      return None

  elif action[0] == 'replace':
    new_file = re.sub( action[1], action[2], file )
    if new_file == file:
      return None

  return new_file



def GenerateRename( actions, file ):
  new_file = file

  for action in actions:
    new_file = DoAction( action, new_file )
    if new_file is None:
      return None

  return ( file, new_file )


def GenerateRenames( actions, files ):
  global verbose
  renames = []

  for file in files:
    rename = GenerateRename( actions, file )
    if rename is not None:
      if rename[1] != "":
        if not os.path.exists( rename[1] ):
          renames.append( rename )
        elif verbose:
          print( "file already exists '{}', dropping".format( rename[1] ) )
      else:
        print( "file's new name is '', dropping" )
    elif verbose:
      print( "skipping incomplete rename '{}'".format( file ) )

  return renames


def FilterRenames( renames, result_re ):
  global verbose
  result = []

  for rename in renames:
    if re.match( result_re, rename[1] ):
      result.append( rename )
    else:
      print( "rename doesn't match result '{}', dropping".format( rename[1] ) )

  return result


def DoRenames( renames ):
  global verbose

  for rename in renames:
    if verbose:
      print( "renaming '{}' -> '{}'".format( rename[0], rename[1] ) )
    os.rename( rename[0], rename[1] )


def AlignOptions( options, padding='  ' ):
  justify = [ 0, 0 ]

  for option in options:
    option[0] = padding + option[0]
    if len( option[0] ) > justify[0]:
      justify[0] = len( option[0] )

    if len( option[1] ) > justify[1]:
      justify[1] = len( option[1] )

  # ensure at least a space between option parts
  justify[0] += 1
  justify[1] += 1

  for option in options:
    option[0] = option[0].ljust( justify[0] )
    option[1] = option[1].ljust( justify[1] )

  indent = justify[0] + justify[1]
  term_width = 80

  try:
    term_width = os.get_terminal_size().columns
  except:
    pass

  for option in options:
    option[2] = textwrap.wrap( option[2], width=term_width-indent )
    option[2] = [ ' '*indent + i if i != option[2][0] else i for i in option[2] ]
    option[2] = '\n'.join( option[2] )


def PrintOptions( options ):
  for option in options:
    print( option[0] + option[1] + option[2] )


def PrintHelp():
  options = [
    [ '-h' , '--help'    , "prints help text then exits." ]                                                    ,
    [ '-v' , '--verbose' , "prints more verbose messages. a really long description that should be wrapped." ] ,
    [ '-d' , '--dryrun'  , "prints what renames would happen without doing them." ]                            ,
    [ '-f' , '--filter=' , "only works with files that match this regex." ]                                    ,
    [ '-r' , '--result=' , "only performs renames that result in a file that matches this regex." ]            ,
    [ '-a' , '--action=' , "add an action to be performed on file names. actions are done in the order they are specified. (see actions)"],
  ]

  AlignOptions( options )

  print( "rename <options> file_one file_two ..." )
  print( "renames files based on python regular expressions" )
  print( "\noptions:" )
  PrintOptions( options )
  print( "\nActions:" )
  print( "  d:regex          | removes all occurances of regex.")
  print( "  r:regex1:regex2  | replaces all occurances of regex1 with regex2.")

  print( "\nExample:" )
  print( "Files:" )
  print( "   'dexter episode 1 [random crap].mp4'")
  print( "   'dexter episode 2 [random crap].mp4'")
  print( "   'dexter episode 3 [random crap].mp4'")
  print( "   'other show episode 1.mp4'")
  print( "\nrename -f 'dexter episode [0-9] \[.*\].mp4' -r 'Dexter E[0-9].mp4' -a 'r:dexter episode ([0-9]) .*:Dexter E\\1.mp4' *")
  print( "\nRenamed files:")
  print( "   'Dexter E1.mp4'")
  print( "   'Dexter E2.mp4'")
  print( "   'Dexter E3.mp4'")


def Main():
  global verbose
  opts, args = getopt( sys.argv[1:], 'hvdf:r:a:', [ 'help', 'verbose', 'dryrun', 'filter=', 'result=', 'action=' ] )
  filter_re  = None
  actions    = []
  dryrun     = False
  result_re  = None

  for opt, arg in opts:
    if opt in [ '-h', '--help' ]:
      PrintHelp()
      exit(0)

    elif opt in [ '-v', '--verbose' ]:
      verbose = true
      print( "verbose mode" )

    elif opt in [ '-d', '--dryrun' ]:
      dryrun = True
      print( "dryrun mode" )

    elif opt in [ '-f', '--filter' ]:
      filter_re = arg
      if verbose:
        print( "file filter '{}'".format( filter_re ) )

    elif opt in [ '-r', '--result' ]:
      result_re = arg
      if verbose:
        print( "resulting names must match '{}'".format( result_re ) )

    elif opt in [ '-a', '--action' ]:
      actions.append( ParseAction( arg ) )

  files   = GetFiles( args, filter_re=filter_re )
  if len( files ) == 0:
    raise Exception( "no files specified" )

  if verbose:
    print( "files:" )
    for file in files:
      print( "  "+file )

  if len(actions) == 0:
    raise Exception( "no actions to do" )

  renames = GenerateRenames( actions, files )

  if result_re is not None:
    renames = FilterRenames( renames, result_re )

  if dryrun:
    for rename in renames:
      print( "{} -> {}".format( rename[0], rename[1] ) )

  else:
    DoRenames( renames )


if __name__ == '__main__':
  Main()