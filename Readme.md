# clgdrive 
 
 
clgdrive is command line interface for google drive. 
 
Currently it only supports: 
  * Listing files 
  * Uploading files and folders 
  * Downloading files, but not folders 
  * Sharing a file or folder with multiple users 
 
It lacks a great deal of features that i would like to implement. 
 
## Installation 
This project uses **_python 3_**, not _python 2_. So make sure to run it with the correct version. 
 
You can start by downloading this repo or clone it into your computer with: 
``` 
git clone https://github.com/cosmeoes/clgdrive.git 
``` 
### Generating client secret 
To use the google drive api you have to have a client id and client secret.
 
To generate them, let's follow this edited version of the [google quickstart guide](https://developers.google.com/drive/v3/web/quickstart/python#step_1_turn_on_the_api_name): 
  1. Use this [wizard](https://console.developers.google.com/start/api?id=drive) to create or select a project in the Google Developers Console and automatically turn on the API. Click Continue, then Go to credentials. 
  2. On the Add credentials to your project page, click the Cancel button. 
  3. At the top of the page, select the OAuth consent screen tab. Select an Email address, enter a Product name if not already set, and click the Save button. 
  4. Select the Credentials tab, click the Create credentials button and select OAuth client ID. 
  5. Select the application type Other, enter the name "cldrive", and click the Create button. 
  6. Click OK to dismiss the resulting dialog.  
  7. Click the file_download (Download JSON) button to the right of the client ID. 
  8. Move this file to directory you downloaded or cloned the project and rename it client_secret.json. 
 
### Dependencies  
This project has the next dependencies: 
- [google-api-python-client](https://developers.google.com/api-client-library/python/) 
- [python-magic](https://github.com/ahupp/python-magic) 
 
You can install them with pip by running: 
``` 
pip install google-api-python-client 
pip install python-magic 
``` 
 
## Usage 
To run clgdrive, run: 
```
python clgdrive.py 
``` 
A browser window will open asking you to log into your google account and give the application permission to manage your drive files. 
Once that is done a interactive shell will appear. 

### Commands.
Here is a list of commands you can use: 

- **cd**: changes the current working directory, it takes an optional argument dir.
  - usage: cd [-h] [dir]
    - dir         Change the working directory 
    - -h, --help  show this help message and exit 
- **ls**: list the files in the given directory, if none is given list the files in the current working directory. 
  - usage: ls [-h] [dir] 
    - dir         the directory to list 
    - -h, --help  show this help message and exit  
- **push**: uploads a file to the current working directory. 
  - usage: push [-h] [-r] files [files ...]    
    - files            the files to upload
    - -h, --help       show this help message and exit 
    - -r, --recursive  upload a directory recursively 
- **pull**: downloads a file from the current working directory. 
  - usage: pull [-h] [-d directory] files [files ...]
    - files                 Files to download  
    - -h, --help            show this help message and exit
    - -d directory, --directory directory   
                                      Specify where to save the file 
- **share**: shares a file with the people with giving emails. 
  - usage: share [-h] files emails [emails ...]   
    - files       The file to share 
    - emails      The people you want to share the file with 
    - -h, --help  show this help message and exit 
 
## Creator comments 
This tool isn't completed and it lacks a lot of features, also, some of the current ones may fail. Keep that in mind while using it. 
 
With that said, you can use or modify the code in this project in any way you want, but that's implicit by publishing in github. 
 
if you have any comments about the project, you can send me an email to: comeoes@gmail.com or make an issue. 

 


