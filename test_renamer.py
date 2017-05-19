#!/bin/python3

import unittest
import renamer
import os


def CreateFile( path ):
  open( path, 'w' ).close()


def CreateFiles( paths ):
  for path in paths:
    CreateFile( path )


def Contains( pattern, source ):
  if source.find( pattern ) < 0:
    return False
  else:
    return True


def RemoveNones( list ):
  while None in list:
    list.remove( None )


class TestGetFiles( unittest.TestCase ):
  @classmethod
  def setUpClass( cls ):
    cls.files = [
      'a-file.file',
      'b-file.file',
      'c file.file',
      'd file.file',
    ]
    CreateFiles( cls.files )


  @classmethod
  def tearDownClass( cls ):
    for file in cls.files:
      os.remove( file )


  def test_ValidFiles_NoFilter( self ):
    # needs a list of valid files
    args = self.files

    files = renamer.GetFiles( args )
    self.assertCountEqual( files, self.files )


  def test_ValidFiles_ReFilter( self ):
    # needs a list of valid files, some with spaces and some without
    args = self.files
    filter_re = '.* .*'

    files = renamer.GetFiles( args, filter_re=filter_re )

    # creates a list of all files that contain a space
    correct_files = [ f if Contains( ' ', f ) else None for f in args ]
    RemoveNones( correct_files )

    self.assertCountEqual( files, correct_files )


  def test_InvalidFiles( self ):
    # requires a list of valid and invalid files, some with spaces some without
    args = [ *self.files, 'invalid file.file' ]
    filter_re = '.* .*'

    files = renamer.GetFiles( args, filter_re=filter_re )

    correct_files = [ f if Contains( ' ', f ) else None for f in self.files ]
    RemoveNones( correct_files )

    self.assertCountEqual( files, correct_files, "\nactual {}\n!=\ncorrect {}".format( files, correct_files ) )


class TestParseAction( unittest.TestCase ):
  def test_remove( self ):
    action = renamer.ParseAction( 'd:a.c' )
    self.assertEqual( action, ( 'remove', 'a.c' ) )


  def test_replace( self ):
    action = renamer.ParseAction( 'r:lang.*\:eng.*:eng')
    self.assertEqual( action, ( 'replace', 'lang.*:eng.*', 'eng' ) )


class TestGenerateRename( unittest.TestCase ):
  def test_order( self ):
    # should rename a-file.file to ile.file only if done in the correct order
    actions = [
      ( 'remove', '-' ),
      ( 'remove', 'af' ),
    ]
    file = 'a-file.file'
    correct_rename = ( file, 'ile.file' )

    new_name = renamer.GenerateRename( actions, file )
    self.assertEqual( new_name, correct_rename, "actions were done out of order" )


  def test_incomplete( self ):
    # should fail and return None because the second action can't be done
    actions = [
      ( 'remove', '-' ),
      ( 'remove', ' ' ),
    ]
    file = 'a-file.file'

    new_name = renamer.GenerateRename( actions, file )
    self.assertIsNone( new_name, "didn't return None on incomplete actions" )


class TestGenerateRenames( unittest.TestCase ):
  def test_( self ):
    files = [
      'a-file.file',
      'b-file.file',
      'c file.file',
      'd file.file',
    ]
    actions = [
      ( 'remove', '-' ),
      ( 'remove', 'af'),
    ]
    correct_renames = [ ( 'a-file.file', 'ile.file' ) ]

    renames = renamer.GenerateRenames( actions, files )
    self.assertCountEqual( renames, correct_renames, "\nactual {}\n!=\ncorrect {}".format( renames, correct_renames ) )
    self.assertEqual( renames[0], correct_renames[0] )


class TestFilterRenames( unittest.TestCase ):
  def test_( self ):
    renames = [
      ( 'abc name 01.file', 'name E01.file' ),
      ( 'abc name 02.file', 'name 02.file' ),
    ]
    result_re = 'name E[0-9]{2}.file'

    renames = renamer.FilterRenames( renames, result_re )
    correct_renames = [
      ( 'abc name 01.file', 'name E01.file' ),
    ]

    self.assertEqual( renames, correct_renames )


class TestDoAction( unittest.TestCase ):
  def test_remove( self ):
    action = ( 'remove', 'll' )
    file   = 'hello world'

    new_file = renamer.DoAction( action, file )
    self.assertEqual( new_file, 'heo world' )


  def test_replace( self ):
    action = ( 'replace', 'll', '!!' )
    file   = 'hello world'

    new_file = renamer.DoAction( action, file )
    self.assertEqual( new_file, 'he!!o world' )


def Main():
  unittest.main( verbosity=2 )


if __name__ == '__main__':
  Main()