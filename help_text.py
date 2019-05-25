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

import keyword_replacer
import fs


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
  replacements = []
  for keyword, func in keyword_replacer.KEYWORDS.items():
    trigger_word = f"{keyword_replacer.KEYWORD_PREFIX}{keyword}"
    replacements.append([trigger_word, '', func.__doc__]) # TODO fix the AlignOptions function so it works with any number of option parts. Then remove this empty string.
  AlignOptions(replacements)


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
  PrintOptions(replacements)
  #print( "  %res  | replaced with WIDTHxHEIGHT of the video" )

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
