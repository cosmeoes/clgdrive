from cmd import Cmd
from argparse import ArgumentParser
from wrapper_cmd_argparser import WrapperCmdLineArgParser
import sys, os
import drive

class ClDrivePrompt(Cmd):
    
    @WrapperCmdLineArgParser()
    def do_push(self, args, parsed, getparser=False):
        if(getparser):
            parser = ArgumentParser(prog="push")
            parser.add_argument("files", nargs='+', help="the files to upload")
            parser.add_argument("-r","--recursive", help="upload a directory recursively", action="store_true")
            return parser

        if(parsed.recursive):
            for directory in parsed.files:
                if(os.path.isdir(directory)):
                    drive.push_dir(directory)
                else:
                    print("%s is not a directory" % directory)
        else:
            drive.push_files(parsed.files)

    @WrapperCmdLineArgParser()
    def do_pull(self, args, parsed, getparser=False):
        if(getparser):
            parser =ArgumentParser(prog="pull")
            parser.add_argument("files", nargs='+', help="Files to download")
            parser.add_argument("-d","--directory", metavar="directory", help="Specify where to save the file")
            parser.add_argument("-r", "--recursive", action="store_true", help="download a folder recursively")
            return parser
        if(parsed.recursive):
            drive.pull_folder(parsed.files)
        elif(parsed.directory):
            if(not os.path.exists(os.path.dirname(parsed.directory))):
                print("Can't find %s" % parsed.directory)
                return
            drive.pull_files_by_name(parsed.files,parsed.directory)
        else:
            drive.pull_files_by_name(parsed.files)


    @WrapperCmdLineArgParser()
    def do_cd(self, args, parsed, getparser=False):
        if(getparser):
            parser = ArgumentParser(prog="cd")
            parser.add_argument("dir",nargs="?", help="Change the working directory")
            return parser
        
        if(not parsed.dir):
            self.prompt = "[MyDrive]> "
            drive.cwd_id = 'root'
            drive.cwd_name = 'MyDrive'
            drive.cwd_parent = 'root'
            return
        if(parsed.dir == ".."):
            parent = drive.get_folder_parent_and_name(drive.cwd_parent)
            self.prompt = "["+parent['name']+"]> "
            drive.cwd_id = drive.cwd_parent
            drive.cwd_name = parent['name']
            drive.cwd_parent = parent['parent']
            return


        folder = drive.find_folder_data(parsed.dir)
        if(folder):
            self.prompt = "["+parsed.dir+"]> "
            drive.cwd_id = folder['id']
            drive.cwd_name = folder['name']
            drive.cwd_parent = folder['parent']
        else: 
            print("%s isn't a directory" % parsed.dir)

    @WrapperCmdLineArgParser()
    def do_ls(self, args, parsed, getparser=False):
        if(getparser):
            parser = ArgumentParser(prog="ls")
            parser.add_argument("dir", nargs='?', help="the directory to list")
            return parser

        if(parsed.dir):
            folder = drive.find_folder_data(parsed.dir)
            if(folder):
                drive.list(folder['id'])
            else:    
                print("%s isn't a directory" % parsed.dir)
        else:
            drive.list(drive.cwd_id)

    @WrapperCmdLineArgParser()
    def do_share(self, args, parsed, getparser=False):
        if(getparser):
            parser = ArgumentParser(prog="share")
            parser.add_argument("files", help="The file to share")
            parser.add_argument("emails", nargs='+', help="The people you want to share the file with")
            return parser

        drive.share_file(parsed.files, parsed.emails)


    def do_quit(self,args):
        """quit: Quits the program"""
        print('bye...')
        sys.exit(0)

    def do_exit(self, args):
        """exit: Quits the program"""
        self.do_quit(args)
   
    def do_EOF(self, args):
        self.do_quit(args)
