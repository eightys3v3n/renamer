import sys
import os
import re


global verbose
try:
  verbose
except NameError:
  verbose = False


def ValidPaths( paths ):
  global verbose
  valid = []

  # searches through the args for files that match the filter expression
  for path in paths:
    # if file exists
    if os.path.exists( path ):
      valid.append( path )

    elif verbose:
      print( "path doesn't exist '{}'".format( path ) )

  return valid


def WalkDirectory( path, recursive=True ):
  """
  Lists all files in given path

  path      | a file or directory path (returns [path] if it is a file)
  recursive | if true, all files inside all folders are returned
              if false, only files directly in path are returned

  Returns a list of files in given path
  """
  global verbose
  files = []

  if os.path.isfile( path ):
    return [ path ]

  try:
    objs = os.listdir( path )

  except PermissionError:
    print( "Permission Denied '{}'".format( path ))
    return []

  for obj in objs:
    if path != '.':
      obj = os.path.join( path, obj )

    if os.path.isfile( obj ):
      files.append( obj )

      if verbose:
        print( "file '{}'".format( obj ), file=sys.stderr )

    elif os.path.isdir( obj ) and recursive:
      files.extend( WalkDirectory( obj ) )

    elif verbose:
      print( "not a file or folder '{}'".format( obj ), file=sys.stderr )

  return files


def ListFiles( paths, recursive=False ):
  """
  Lists all files in given paths.

  paths     | a list of file or directory paths
  recursive | if true, all files inside all folders are returned
              if false, only files directly in folders specified are returned

  Returns a list files in given paths
  """
  files = []

  for path in paths:
    files.extend( WalkDirectory( path, recursive=recursive ) )

  return files


def FilterFiles( files, filter ):
  global verbose
  new_files = []

  for file in files:
    if re.match( filter, file ):
      new_files.append( arg )

    elif verbose:
      print( "file doesn't match filter '{}'".format( arg ) )

  return new_files


def GetFiles( args, filter_re=None, recursive=False ):
  """
  Lists args that are files and match the filter expression.

  args      | a list of file paths and possibly other junk. only files that exist are returned.
  filter_re | a regular expression used to filter out args

  Returns a list of the args that are existing files and that match filter_re.
  """
  global verbose

  paths = ValidPaths( args )
  paths = ListFiles( args, recursive=recursive )

  if filter_re is not None:
    paths = FilterFiles( paths, filter_re )

  return paths