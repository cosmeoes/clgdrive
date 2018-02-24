from cmd import Cmd
import sys
import httplib2
from apiclient import discovery
from getAuth import get_credentials
#get the credentials for google drive 
credentials = get_credentials() 

class ClDrivePrompt(Cmd):

    def do_ls(self, args):
        """ls: lists the files in a directory, it takes as a parameter the directory path. 
        if the path isn't given, it list the files in the current directory"""

        if(len(args)>0):
            print('thats a nice directroy you have there, but i don\'t know how to do that yet')
        else:
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('drive', 'v3', http=http)

            results = service.files().list(
                pageSize=10,fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])
            if not items:
                print('No files found.')
            else:
                print('Files:')
                for item in items:
                    sys.stdout.buffer.write(('{0} ({1})\n'.format(item['name'], item['id']).encode('utf-8')))

    def do_quit(self,args):
        """quit: Quits the program"""
        print('\nbye...')
        sys.exit(0)

    def do_exit(self, args):
        """exit: Quits the program"""
        self.do_quit(args)
     
