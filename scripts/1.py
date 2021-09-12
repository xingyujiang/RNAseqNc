from pathlib import Path


home = '/home/jy'
dir = 'dir/'
file = '123.txt'
print(Path(home, file))
print(Path(home, dir))
print(Path(home +"/" + dir))
dir=[]
print(dir)