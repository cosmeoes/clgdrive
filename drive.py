import httplib2, sys, os
import magic 
from apiclient import discovery, errors
from getAuth import get_credentials
from apiclient.http import MediaFileUpload 
#get the credentials for google drive 
credentials = get_credentials() 
cwd_id = "root"
cwd_name = "MyDrive"
cwd_parent = "root"
def list(folder):
    service = get_service()
    page_token = None

    while True:
        response = service.files().list(q="'"+folder+"' in parents",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            sys.stdout.buffer.write(('{0} \n'.format(file.get('name'))).encode('utf-8'))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
        else:
            sys.stdout.write('\rPress enter to continue listing files or Ctrl+c to quit')
            sys.stdout.flush()
            input()

            
def find_folder_id(name):
    service = get_service()
    response = service.files().list(q="name='"+name+"' and '"+cwd_id
                                    +"' in parents and mimeType='application/vnd.google-apps.folder'",
                                    fields='files(id, name, createdTime, parents)').execute()
    folders = []
    for file in response.get('files', []):
        folders.append({'id': file.get('id'),'name': file.get('name'), 'createdTime': file.get('createdTime'), 'parent': file.get('parents')[0]})

    if(not folders):
        return None
    if(len(folders)==1):
        return folders[0]
    else:
        print("There are multiple directories with the same name:")
        for index, folder in enumerate(folders):
            sys.stdout.write(str(index+1) +") %s created: %s\n" % (folder['name'], str(folder['createdTime'])))

        while True:
            try:
                selection = int(input("Enter an option number: "))
                return folders[selection]
                break;
            except ValueError:
                pass     

def get_folder_parent_and_name(id):
    service = get_service()
    response = service.files().get(fileId=id,
                                    fields='name, parents').execute()
    
    return {'name': response.get('name'), 'parent': response.get('parents')[0] if(response.get('parents')) else 'root'}
    
def push_file(filename, parent=None):
    """Uploads a file to google drive"""
    if(os.path.isdir(filename)):
        print("%s is a directory, use: push -r %s to upload recursively" % (filename, filename))
        return;
    if(not os.path.isfile(filename)): 
        print("Can not find %s, no such file" % filename)
        return;

    mimetype = magic.from_file(filename, mime=True) 
    media = None
    name = os.path.basename(filename)
    service = get_service();
    body = {
        'name': name,
        'parents': [parent] if(parent) else None
    }
    if(not mimetype == 'inode/x-empty'):
        media = MediaFileUpload(filename, mimetype = mimetype, resumable=True)
        request = service.files().create(body=body, media_body=media)
        response = None
        while response is None:
            uplodadtry = 0
            try:
                status, response = request.next_chunk()
            except errors.HttpError as e:
                if(e.resp.status in [404]):
                    # Start the upload all over again.
                    print("An error ocurred, restarting upload")
                    push_file(filename)
                elif(e.resp.status in [500, 502, 503, 504] and uploadtry < 6):
                    # Call next_chunk() again, but use an exponential backoff for repeated errors.
                    uploadtry += 1
                    exponetialBackoff(uploadtry)
                    continue;
                else:
                    print("File not uploaded: %s" % filename, e)
                    return;
            if status:
                progress = int(status.progress() * 100)
                sys.stdout.write("\rUploading %s: %d%%" % (filename, progress))
                sys.stdout.flush()
    else:
        try:
            request = service.files().create(body=body).execute()
        except:
            print("File not uploaded: %s" % filename)
            return;
    sys.stdout.write(" %s uploaded\n" % filename)


def push_files(files, parent=None):
    """Uploads a list of files to google drive""" 
    for filename in files:    
        push_file(filename, parent)

def push_dir(directory, parent=None):
    """Uploads a directory to google drive"""
    service = get_service()
    foldername = os.path.dirname(os.path.basename(directory)+"/")
    file_metadata = {
        'name': foldername,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent] if(parent) else None,
    }
    folder = service.files().create(body=file_metadata,
                                        fields='id').execute()

    print("%s folder created" % foldername)
    folderid = folder.get('id')
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if(os.path.isdir(filepath)):
            push_dir(filepath, folderid)
        else:
            push_file(filepath, folderid)

def get_service():
    http = credentials.authorize(httplib2.Http())        
    service = discovery.build('drive', 'v3', http=http)
    return service
                    
def exponetialBackoff(n):
    time.sleep((2 ** n) + (random.randint(0, 1000) / 1000))
