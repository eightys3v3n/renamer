#!/bin/python3


"""
  Written by Terrence = eightys3v3n@gmail.com
"""


from getopt import getopt
import keyword_replacer
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
  """
  Lists args that are files and match the filter expression.

  args      | a list of file paths and possibly other junk. only files that exist are returned.
  filter_re | a regular expression used to filter out args

  Returns a list of the args that are existing files and that match filter_re.
  """
  global verbose
  files   = []
  Matches = None  # a function. returns True if file matches filter expression.

  # sets the Matches function
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

  # searches through the args for files that match the filter expression
  for arg in args:

    # if file exists
    if os.path.isfile( arg ):

      # if it matches the filter expression
      if Matches( filter_re, arg ):
        files.append( arg )
      elif verbose:
        print( "file doesn't match filter '{}'".format( arg ) )
    elif verbose:
      print( "file doesn't exist '{}'".format( arg ) )

  return files


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

    # split the string with :
    # do not split on a \:
    res = re.split( '(?<!\\\):', raw )

    # replace all the \: with :
    # they had to be escaped in the command so as to not split in the wrong place
    res[0] = res[0].replace( '\\:', ':' )   # replace this
    res[1] = res[1].replace( '\\:', ':' )   # with this

    action.extend( res )

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

  # remove some bits
  if action[0] == 'remove':
    # didn't see a remove function so actually just replacing with nothing
    new_file = re.sub( action[1], '', file )

    if not partial and new_file == file:
      return None

  # same as above but replace some bits
  elif action[0] == 'replace':
    new_file = re.sub( action[1], action[2], file )

    if not partial and new_file == file:
      return None

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


def PrintHelp():
  """
  Prints the help text
  """
  options = [
    [ '-h' , '--help'    , "prints help text then exits." ]                                                    ,
    [ '-v' , '--verbose' , "prints more verbose messages. a really long description that should be wrapped." ] ,
    [ '-d' , '--dryrun'  , "prints what renames would happen without doing them." ]                            ,
    [ '-f' , '--filter=' , "only works with files that match this regex." ]                                    ,
    [ '-r' , '--result=' , "only performs renames that result in a file that matches this regex." ]            ,
    [ '-a' , '--action=' , "add an action to be performed on file names. actions are done in the order they are specified. (see actions)" ],
    [ '-p' , '--partial' , "allows for only some of the specified actions to be applied to file names" ],
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

  # parse the command line options and arguments
  opts, args = getopt( sys.argv[1:], 'hvdf:r:a:p', [ 'help', 'verbose', 'dryrun', 'filter=', 'result=', 'action=', 'partial' ] )
  filter_re  = None
  actions    = []
  dryrun     = False
  result_re  = None
  command    = None
  partial    = False

  # parse command line arguments
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
      # add ( action_type, action_arguments... ) to actions
      actions.append( ParseAction( arg ) )

    elif opt in [ '-p', '--partial' ]:
      partial = True


  # get the files that will be worked with
  files   = GetFiles( args, filter_re=filter_re )
  if len( files ) == 0:
    raise Exception( "no files specified" )


  # print errors if required arguments are missing
  if len(actions) == 0:
    raise Exception( "no actions to do" )


  # print the files we will work with, if verbose is on
  if verbose:
    print( "files:" )
    for file in files:
      print( "  "+file )


  # generate a list of ( original_file_name, new_file_name )
  renames = GenerateRenames( actions, files, partial=partial )


  # filter out renames whose new_file_name doesn't match the result expression
  if result_re is not None:
    renames = FilterRenames( renames, result_re )

  if dryrun:
    for rename in renames:
      print( "{} -> {}".format( rename[0], rename[1] ) )

  else:
    # actually rename all the files
    DoRenames( renames )


if __name__ == '__main__':
  Main()