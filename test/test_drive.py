import sys,os
import drive
import unittest

class TestDrive(unittest.TestCase):
    
    def test_make_file_path(self):
        self.assertEqual(drive.make_file_path('/folder/filename.txt', 'file.txt'), '/folder/filename.txt')
        self.assertEqual(drive.make_file_path('/file/path/', 'filename.txt'), "/file/path/filename.txt")
        folder= "path"
        os.makedirs(folder)
        self.assertEqual(drive.make_file_path(folder, "filename.txt"), "path/filename.txt")
        os.rmdir(folder)

