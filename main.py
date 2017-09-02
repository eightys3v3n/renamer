#!/bin/python3

"""
Written by Terrence, eightys3v3n@gmail.com
"""


from getopt import getopt
import unittest
import textwrap
import shutil
import sys
import os
import re

# appends the path of the script to the path environment
# this allows the script to be run from working directories other than where it is
sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) )

import keyword_replacer
import fs


global verbose, true, false
true  = True
false = False
verbose = false


def ParseAction( raw ):
  """
  Parses an action in the form of a string.

  raw | a string that represents the action that should be taken

  Returns a tuple
  """
  # action[0] is always the type of action (remove, replace, ...)
  # action's length depends on what type of action is being performed.
  action = [ '' ]

  # remove action
  if raw[0:2] == 'd:':
    # set the type of action
    action[0] = 'remove'
    raw = raw[2:]

    # the rest of the string is the regex that should be removed
    action.append( raw )

  # replace action
  elif raw[0:2] == 'r:':
    # set the type of action
    action[0] = 'replace'
    raw = raw[2:]

    # split the string with ':'
    # do not split on '\:'
    res = re.split( '(?<!\\\):', raw )

    if len(res) != 2:
      raise Exception( "too many seperators ':'", raw )

    # replace all the \: with :
    # they had to be escaped in the command so as to not split in the wrong place
    res[0] = res[0].replace( '\\:', ':' )   # replace this
    res[1] = res[1].replace( '\\:', ':' )   # with this

    action.extend( res )

  # insert action
  elif raw[0:2] == 'i:':
    action[0] = 'insert'
    raw = raw[2:]

    # split string with ':'
    # do not split on '\:'
    res = re.split( '(?<!\\\):', raw )

    # no position to insert at was specified
    if len(res) == 1:
      action.extend( [ 0, res[0] ] )

    # a position to insert at was specified
    elif len(res) == 2:
      # try to convert the position to an int
      try:
        i = int( res[0] )
      except ValueError:
        raise Exception( "in 'i:int:abc' int must be a signed integer", res[0] )

      action.extend( [ i, res[1] ] )

    else:
      raise Exception( "too many seperators ':'", raw )

  elif raw[0:2] == 'a:':
    action[0] = 'append'
    raw = raw[2:]

    action.append( raw )

  else:
    raise Exception( "invalid action", raw[0:2] )

  return tuple( action )


def DoAction( action, file, partial=False ):
  """
  Does the specified action to the file name.

  action | a tuple ( action_to_be_done, arguments_for_that_action )
  file   | the file path or name to change

  Returns the changed file name.
  """
  new_file = None

  # remove some stuff
  if action[0] == 'remove':
    # didn't see a remove function so actually just replacing with nothing
    new_file = re.sub( action[1], '', file )

    if not partial and new_file == file:
      return None

  # same as above but replace some stuff
  elif action[0] == 'replace':
    new_file = re.sub( action[1], action[2], file )

    if not partial and new_file == file:
      return None

  # inserts new stuff at position action[1]
  elif action[0] == 'insert':
    # if the insert position is outside of the file name
    if action[1] > 0:
      if action[1] >= len( file ):
        new_file = file
    else:
      if action[1]*-1 >= len( file ):
        new_file = file

    # if the insert position is a real position in the file name, insert the stuff there
    if new_file is None:
      prefix = file[ 0:action[1] ]
      suffix = file[ action[1]: ]
      new_file = prefix + action[2] + suffix

    if not partial and new_file == file:
      return None

  # append new stuff at the end of the name, before the extension (if any)
  elif action[0] == 'append':
    ext_i = file.rfind( os.path.extsep )
    extension = ''

    if ext_i < 0:
      new_file = file
    else:
      extension = file[ ext_i: ]
      new_file  = file[ 0 : ext_i ]

    new_file += action[1] + extension

  return new_file


def GenerateRename( actions, file, partial=False ):
  """
  Performs a list of actions on a file name.

  actions | a list of ( action_to_be_done, arguments_for_that_action )
  file    | file name or path to change

  Returns the new file name.
  """
  new_file = file

  for action in actions:
    new_file = DoAction( action, new_file, partial=partial )

    # if the action didn't change the file name let the calling function deal with it.
    # stops on first failed action to prevent renaming things you didn't intend to in a wierd way.
    if new_file is None:
      return None

  new_file = keyword_replacer.ReplaceKeyWords( new_file, file )

  return ( file, new_file )


def GenerateRenames( actions, files, partial=False ):
  """
  Performs a list of actions on a list of file names.

  actions | a list of ( action_to_be_done, arguments_for_that_action )
  files   | a list of file names or paths

  Returns a list of ( original_file_name, new_file_name )
  """
  global verbose
  renames = []

  for file in files:
    # generate ( original_file_name, new_file_name )
    rename = GenerateRename( actions, file, partial=partial )

    # if the new file name is the same as the old,
    # don't touch that file.
    if rename is not None:

      # just an extra meassure. Don't rename something to some common mistake file names
      if rename[1] not in [ '', '.', '..', '/' ]:

        # if a file with the new name already exists, warn and skip this file
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
  """
  Remove any rename attempts that don't match the result expression

  renames   | an array of ( original_name, new_name )
  result_re | a regular expression

  Returns a list of renames that match the result expression
  """
  global verbose
  result = []

  for rename in renames:
    # if the destination name matches the result expression
    if re.match( result_re, rename[1] ):
      result.append( rename )

    else:
      print( "rename doesn't match result '{}', dropping".format( rename[1] ) )

  return result


def DoRenames( renames ):
  """
  Rename all the given files

  renames | an array of ( current_name, desired_name )

  Returns None
  """
  global verbose

  for rename in renames:
    if verbose:
      print( "renaming '{}' -> '{}'".format( rename[0], rename[1] ) )

    os.rename( rename[0], rename[1] )


def AlignOptions( options, padding='  ' ):
  """
  Given an array of options, add the padding to all of them and line up the second and third options

  options | an array of [ short_option, long_option, description ]
  padding | add the padding to the beginning of short_option for every option

  Returns None
  Modifies options
  """
  justify = [ 0, 0 ]

  # put the longest short_option in justify[0]
  # put the longest long_option in justify[1]
  for option in options:
    # add the padding to the first option
    option[0] = padding + option[0]

    if len( option[0] ) > justify[0]:
      justify[0] = len( option[0] )

    if len( option[1] ) > justify[1]:
      justify[1] = len( option[1] )

  # ensure at least a space between the short and long, long and description
  justify[0] += 1
  justify[1] += 1

  # justify the short and long options so their beginings line up nicely
  for option in options:
    option[0] = option[0].ljust( justify[0] )
    option[1] = option[1].ljust( justify[1] )

  # if the description wraps to the next line, how far should it be indented to
  # be in line with the first line.
  indent = justify[0] + justify[1]

  # terminal width, default 80
  term_width = 80

  # try to get the terminal width and use that for text wrapping
  try:
    term_width = os.get_terminal_size().columns
  except:
    pass

  # wrap all the descriptions
  for option in options:
    option[2] = textwrap.wrap( option[2], width=term_width-indent )
    option[2] = [ ' '*indent + i if i != option[2][0] else i for i in option[2] ]
    option[2] = '\n'.join( option[2] )


def PrintOptions( options ):
  """
  print( option[i][0] + option[i][1] + option[i][2] )
  """
  for option in options:
    print( option[0] + option[1] + option[2] )


def PrintHelp( options ):
  """
  Prints the help text
  """
  options = [
    [ '-h', '--help'     , "prints help text then exits." ],
    [ '-v', '--verbose'  , "prints more verbose messages. a really long description that should be wrapped." ],
    [ '-d', '--do'       , "actually renames files; does dry run by default." ],
    [ '-f', '--filter='  , "only works with files that match this regex." ],
    [ '-R', '--result='  , "only performs renames that result in a file that matches this regex." ],
    [ '-a', '--action='  , "add an action to be performed on file names. actions are done in the order they are specified. (see actions)" ],
    [ '-p', '--partial'  , "allows for only some of the specified actions to be applied to file names" ],
    [ '-r', '--recursive', "scan directories recursively" ],
  ]

  AlignOptions( options )

  print( "rename <options> file_one file_two ..." )
  print( "renames files based on python regular expressions" )
  print( "\noptions:" )
  PrintOptions( options )
  print( "\nActions:" )
  print( "  d:regex          | removes all occurances of regex.")
  print( "  r:regex1:regex2  | replaces all occurances of regex1 with regex2.")
  print( "  i:position:text  | inserts text at position. negative position starts from the end.")
  print( "  a:text           | appends text to the end of the name, before the extension.")
  print( "\nReplacements:" )
  print( "  %res  | replaced with WIDTHxHEIGHT of the video" )

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

  # parse the command line options and arguments
  options = {
    'short':'hvdf:R:a:pr',
    'long' :[
      'help',
      'verbose',
      'do',
      'filter=',
      'result=',
      'action=',
      'partial',
      'recursive',
    ],
  }
  opts, args = getopt( sys.argv[1:], options['short'], options['long'] )
  actions    = []
  filter_re  = None
  result_re  = None
  command    = None
  specific_files = False
  recursive      = False
  partial        = False
  dryrun         = True

  # parse command line arguments
  for opt, arg in opts:
    if opt in [ '-h', '--help' ]:
      PrintHelp(options)
      exit(0)

    elif opt in [ '-v', '--verbose' ]:
      verbose = true
      print( "verbose mode" )

    elif opt in [ '-d', '--do' ]:
      dryrun = False

    elif opt in [ '-f', '--filter' ]:
      filter_re = arg
      if verbose:
        print( "file filter '{}'".format( filter_re ) )

    elif opt in [ '-R', '--result' ]:
      result_re = arg
      if verbose:
        print( "resulting names must match '{}'".format( result_re ) )

    elif opt in [ '-a', '--action' ]:
      # add ( action_type, action_arguments... ) to actions
      actions.append( ParseAction( arg ) )

    elif opt in [ '-p', '--partial' ]:
      partial = True

    elif opt in [ '-r', '--recursive' ]:
      recursive = True


  if verbose:
    print( "getting files" )
  # get the files that will be worked with
  if args == []:
    args = ['.']
  files = fs.GetFiles( args, filter_re=filter_re, recursive=recursive )
  if len( files ) == 0:
    raise Exception( "no files found" )


  # print errors if required arguments are missing
  if len(actions) == 0:
    raise Exception( "no actions to do" )


  # print the files we will work with, if verbose is on
  if verbose:
    print( "files:" )
    for file in files:
      print( "  "+file )


  if verbose:
    print( "generating renames" )
  # generate a list of ( original_file_name, new_file_name )
  renames = GenerateRenames( actions, files, partial=partial )

  if verbose:
    print( "sorting renames" )
  renames.sort()

  if verbose:
    print( "filtering renames" )
  # filter out renames whose new_file_name doesn't match the result expression
  if result_re is not None:
    renames = FilterRenames( renames, result_re )

  if dryrun:
    for rename in renames:
      print( "{} -> {}".format( rename[0], rename[1] ) )

  else:
    if verbose:
      print( "doing renames" )
    # actually rename all the files
    DoRenames( renames )


if __name__ == '__main__':
  Main()