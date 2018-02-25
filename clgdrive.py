import sys
from command_prompt import ClDrivePrompt
import drive

def main():
    prompt= ClDrivePrompt() 
    prompt.prompt = "["+drive.cwd_name+"]> "
    prompt.cmdloop()

def catch_ctrl_c():
    try:
        main()
    except KeyboardInterrupt:
        print('\n')
        catch_ctrl_c()


if __name__ == '__main__':
    catch_ctrl_c()
