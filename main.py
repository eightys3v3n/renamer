#!/usr/bin/python3

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

import help_text
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
      help_text.PrintHelp(options)
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
