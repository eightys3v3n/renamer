import os
import re


def GetValidFiles( args ):
  files = []

  for arg in args:
    # if file exists
    if os.path.isfile( arg ):
      files.append( arg )

  return files





def GetFiles( args, filter_re=None, recursive=False, specific=False ):
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