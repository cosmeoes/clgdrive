import sys
from command_prompt import ClDrivePrompt, credentials

def main():
    prompt= ClDrivePrompt() 
    prompt.prompt = "[ClDrive]> "
    prompt.cmdloop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print ('bye..')
        sys.exit(0)
