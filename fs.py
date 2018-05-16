import os
import subprocess
import glob
import shutil
import sys

def join(dir, *file):
  return os.path.join(dir, *file)

def pathExist(path):
  return os.path.exists(path)

def isWildCard(path):
  return path.find("*") != -1
  
def move(src, dst):
  # wildcard
  if isWildCard(src):
    files = findFiles(src)
    for file in files:
      dstPath = join(dst, fileName(file))
      if pathExist(dstPath):
        remove(dstPath)
      shutil.move(file, dst)
    return

  path = join(dst, fileName(src))
  if os.path.isfile(path):
    if pathExist(path):
      remove(path)
  shutil.move(src, dst)

def mkDir(path):
  if not os.path.exists(path):
    os.mkdir(path)

def rmDir(path):
  if os.path.exists(path):
    shutil.rmtree(path)

def rename(src, dst):
  os.rename(src, dst)

def extension(file):
  path, ext = os.path.splitext(file)
  return ext

def changeExtension(file, newExtension):
  path, ext = os.path.splitext(file)
  return path + newExtension

def pathExistList(dirs):
  errors = []
  for path in dirs:
    if not os.path.exists(path):
      errors.append(path)

  for error in errors:
    print("NotFoundPath: " + error)
  
  return len(errors) == 0

def pathExistDictionary(dic):
  errors = []
  for k, v in dic.iteritems():
    if not os.path.exists(v):
      errors.append(k + " => " + v)
  if len(errors) != 0:
    for error in errors:
      print("NotFoundPath: " + error)
  return len(errors) == 0

def cd():
  return os.getcwd()

def fullPath(*path):
  return os.path.abspath(os.path.join(os.getcwd(), *path))

def fullPathUpdate(dic):
  temp = {}
  for k, v in dic.iteritems():
    temp[k] = fullPath(v)
  dic.update(temp) 

def runCommand(*args):
  message = ' '.join(args)
  process = subprocess.Popen(message, shell=True)
  ret = process.wait()
  return ret

# get absolute directory
def getDir(path):
  files = os.listdir(fullPath(path))
  return [fullPath(path, file) for file in files if os.path.isdir(fullPath(path, file))]

def fileName(path):
  return os.path.basename(path)

def isEmpty(str):
  return len(str) == 0

# wild card
def findFiles(dir, wildcard=""):
  if isEmpty(wildcard):
    return glob.glob(dir)
  return glob.glob(join(dir, wildcard))

def readFile(path):
  with open(path) as file:
    return file.read()

def writeFile(path, message, mode = "w"):
  with open(path, mode) as file:
    file.write(message)

def cleanup(path):
  files = glob.glob(path);
  for file in files:
    os.remove(file)

def remove(path):
  if pathExist(path):
    os.remove(path)

def copy(file, dstDir):
  shutil.copyfile(file, join(dstDir, fileName(file)))
