import httplib2, sys, os, io
import magic 
from apiclient import discovery, errors
from getAuth import get_credentials
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
#get the credentials for google drive 
credentials = get_credentials() 
cwd_id = "root"
cwd_name = "MyDrive"
cwd_parent = "root"

def list(folder, trashed="false", sharedWithme=False):
    page_token = None
    while True:
        files, page_token = get_files_form_folder(folder,page_token=page_token, trashed=trashed, sharedWithme=sharedWithme)
        for file in files:
            sys.stdout.buffer.write(('{0} \n'.format(file.get('name'))).encode('utf-8'))

        if(not page_token):
            return

        sys.stdout.write('\rPress enter to continue listing files or Ctrl+c to quit')
        sys.stdout.flush()
        input()
   

def get_files_form_folder(folder, page_token=None, all=False, trashed='false', sharedWithme=False):
    service = get_service()
    files = []
    while True:
        response = service.files().list(q="'"+folder+"' in parents and trashed = "+trashed+(" and sharedWithMe" if sharedWithme else ""),
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name, mimeType)',
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            files.append(file)

        if(not all):
            page_token = response.get('nextPageToken', None)
            return files, page_token

        if page_token is None:
            break

    return files




def share_callback(request_id, response, exception):
    if exception:
        # Handle error
        print(exception)
    else:
        print("File shared")


def share_file(filename, emails):
    fileid = find_file_id(filename)['id']
    service = get_service()
    batch = service.new_batch_http_request(callback=share_callback)
    for email in emails:
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        batch.add(service.permissions().create(
                fileId=fileid,
                body=user_permission,
                fields='id',
        ))
    batch.execute()
 
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
                    print("Error: %s not downloaded" % filename, e)
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
    sys.stdout.write("\n %s uploaded\n" % filename)


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

def download_file_by_id(filename, file_id):
    service = get_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    downloadtry = 0
    while done is False:
        try:
            status, done = downloader.next_chunk()
        except errors.HttpError as e:
            if(e.resp.status in [404]):
                # Start the upload all over again.
                print("An error ocurred, restarting download")
                return download_file_by_id(filename)
            elif(e.resp.status in [500, 502, 503, 504] and uploadtry < 6):
                downloadtry += 1
                exponetialBackoff(downloadtry)
                continue
            elif(e.resp.status == 416):
                sys.stdout.write("%s understood as a 0 bytes file" % filename)
                return fh
            else:
                print("Error: %s not downloaded" % filename, e)
                return
        
        progress = int(status.progress() * 100)
        sys.stdout.write("\rDownloading %s: %d%%" % (filename, progress))
        sys.stdout.flush()
    return fh
    
def write_file_to_disk(file_to_write, data_bytes):
    with open(file_to_write, 'wb') as file:
        file.write(data_bytes)

def pull_files_by_id(filelist, topath="./"):
    for file in filelist:
        filename = file['name']
        file_id = file['id']
        fh = download_file_by_id(filename,file_id)
        if(not fh): return
        output_file = make_file_path(topath, filename)
        sys.stdout.write("\n%s downloaded\n" % filename)
        write_file_to_disk(output_file, fh.getvalue())

def pull_files_by_name(filelist, topath="./"):
    file_list = []
    for file in filelist:
        file_list.append(find_file_id(file))
    pull_files_by_id(file_list, topath) 

def pull_folder(folders, topath="./", parent=cwd_id):
    for folder in folders:
        if(not os.path.exists(topath)):
            print("Error: %s can't find" % topath)
            return 
        folderpath = os.path.join(topath, folder)
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)
            print("Created directory %s" % folderpath)
        folder_data = find_folder_id(folder, parent)
        files = get_files_form_folder(folder_data['id'], all=True)
        fileid_list = []
        for file in files:
            if(file['mimeType']=='application/vnd.google-apps.folder'):
                pull_folder([file['name']], folderpath, folder_data['id'])
            else:
                fileid_list.append(file)
        pull_files_by_id(fileid_list, folderpath)

def make_file_path(path, filename):
    return path if os.path.basename(path) and not os.path.isdir(path) else os.path.join(path, filename)

def get_service():
    http = credentials.authorize(httplib2.Http())        
    service = discovery.build('drive', 'v3', http=http)
    return service
                    
def exponetialBackoff(n):
    time.sleep((2 ** n) + (random.randint(0, 1000) / 1000))

def find_folder_id(name, parent=cwd_id):
    return find_file_id(name, mimetype='application/vnd.google-apps.folder', parent=parent)
         
def find_file_id(name, mimetype=None, parent=cwd_id):
    service = get_service()
    response = service.files().list(q="name='"+name+"' and '"+parent
                                    +"' in parents" + (" and mimeType='"+mimetype+"'" if mimetype else ""),
                                    fields='files(id, name, createdTime, parents)').execute()
    files = []
    for file in response.get('files', []):
        files.append({'id': file.get('id'),'name': file.get('name'), 'createdTime': file.get('createdTime'), 'parent': file.get('parents')[0]})

    if(not files):
        return None
    if(len(files)==1):
        return files[0]
    else:
        print("There are multiple options with the same name:")
        for index, file in enumerate(files):
            sys.stdout.write(str(index+1) +") %s created: %s\n" % (file['name'], str(file['createdTime'])))

        while True:
            try:
                selection = int(input("Enter an option number: "))
                return files[selection]
                break;
            except ValueError:
                pass


def get_folder_parent_and_name(id):
    service = get_service()
    response = service.files().get(fileId=id,
                                    fields='name, parents').execute()
    
    return {'name': response.get('name'), 'parent': response.get('parents')[0] if(response.get('parents')) else 'root'}
