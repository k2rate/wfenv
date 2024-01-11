from termcolor import colored

def colpath(str):
    return colored(f'{str}', "light_magenta")

def colwarn(str):
    return colored(f'{str}', "red")

def colwinname(str):
    return colored(f'{str}', "green")

def colwinclass(str):
    return colored(f'{str}', "green")

def colsignature(str):
    return colored(f'{str}', "yellow")