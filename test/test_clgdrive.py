import unittest, os, sys
import command_prompt
from unittest.mock import patch
import drive

class TestCommandPrompt(unittest.TestCase):
    
    def test_do_push(self):
        with patch('command_prompt.print') as mocked_print:
            command_prompt.ClDrivePrompt.do_push(None,"-r dirname")
            mocked_print.assert_called_with('dirname is not a directory')
        with patch('command_prompt.drive.push_dir') as mocked_push_dir:
            os.makedirs('dirname')
            command_prompt.ClDrivePrompt.do_push(None,"-r dirname")
            mocked_push_dir.assert_called_with('dirname')
            os.rmdir('dirname')


class TestDrive(unittest.TestCase):
    
    def test_make_file_path(self):
        self.assertEqual(drive.make_file_path('/folder/filename.txt', 'file.txt'), '/folder/filename.txt')
        self.assertEqual(drive.make_file_path('/file/path/', 'filename.txt'), "/file/path/filename.txt")
        folder= "path"
        os.makedirs(folder)
        self.assertEqual(drive.make_file_path(folder, "filename.txt"), "path/filename.txt")
        os.rmdir(folder)


