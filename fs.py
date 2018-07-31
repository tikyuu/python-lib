# coding:utf-8
import os
import subprocess
import glob
import shutil
import sys
import filecmp
import logging

"""
必要なファイル操作をまとめた自作モジュール fs (file system)

batファイルでできることを一通りそろえてみた

docコメントの型
- int
- bool ※ pythonのbool型の値は True, False の先頭大文字
- string
- T[] (リスト型)
- [T, T] (ディクショナリ型)
- * string (可変長引数 (リストとほぼ同じ))
"""

LOG_FILE = 'build.log'
class Logging:
  """
  ログファイルを書き込むクラス
  設定がめんどうなのでクラス化しました
  出力フォーマットとか変更できます。
  """

  def __init__(self, file_name):
    self.logger = logging.getLogger('Logging')
    self.logger.setLevel(10)
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)

    fh = logging.FileHandler(log_path)
    self.logger.addHandler(fh)

    sh = logging.StreamHandler()
    self.logger.addHandler(sh)

    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)

  def write(self, message):
    self.logger.log(20, message)

logging = Logging(LOG_FILE)

def log(message):
  """
  ログファイルにメッセージを追加する
  @param string message
  """
  logging.write(message)

def join(dir, *file):
  """
  パスを結合する
  @param string dir
  @param * string file
  @return string 結合されたパス名
  """
  return os.path.join(dir, *file)

def pathExist(path):
  """
  パスが存在するか調べる
  @param string path
  @return bool
  """
  return os.path.exists(path)

def isWildCard(str):
  """
  ワイルドカードの有無を調べる
  @param string str
  @return bool
  """
  return str.find("*") != -1
  
def move(src, dst):
  """
  ファイルを移動する
  @param string src 正規表現可
  @param string dst
  """
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
  """
  ディレクトリを生成する (既に存在する場合なにもしない)
  @param string path
  """
  if not os.path.exists(path):
    os.mkdir(path)

def rmDir(path):
  """
  ディレクトリを削除する (存在しない場合なにもしない)
  @param string path
  """
  if os.path.exists(path):
    shutil.rmtree(path)

def rename(src, dst):
  """
  ファイル名を変更する
  @param string src
  @param string dst
  """
  remove(dst)
  os.rename(src, dst)

def extension(file):
  """
  ファイルの拡張子を取得する
  @param string file
  @return string
  """
  path, ext = os.path.splitext(file)
  return ext

def changeExtension(file, newExtension):
  """
  ファイルの拡張子を変更した文字列の取得
  @param string file
  @param string newExtension
  @return string 拡張子を変更したファイル名
  """
  path, ext = os.path.splitext(file)
  return path + newExtension

def pathExistList(dirs):
  """
  リスト型のパスが存在する確認する
  @param string[] dirs
  @return bool true = 全て存在する, false = 失敗
  """
  errors = []
  for path in dirs:
    if not os.path.exists(path):
      errors.append(path)

  for error in errors:
    print("NotFoundPath: " + error)
  
  return len(errors) == 0

def pathExistDictionary(dic):
  """
  辞書型の値のパスが存在する確認する
  @param [T, string] dic
  @return bool true = 全て存在する, false = 失敗
  """
  errors = []
  for k, v in dic.iteritems():
    if not os.path.exists(v):
      errors.append(k + " => " + v)
  if len(errors) != 0:
    for error in errors:
      print("NotFoundPath: " + error)
  return len(errors) == 0

def moveCd(path):
  """
  カレントディレクトリを移動する
  @param string path 移動する場所
  """
  os.chdir(path)

def cd():
  """
  カレントディレクトリを取得する
  @return string
  """
  return os.getcwd()

def getRunCd(_file):
  """
  現在実行しているファイルのディレクトリを取得する
  %~dp0と同じ処理になる
  @param string file ※ __file__を必ず渡す必要がある 
  return string
  """
  return os.path.dirname(os.path.abspath(_file))

def getRunCdRelative(file):
  """
  フルパスの現在実行しているファイルのディレクトリ名からディレクトリのみに変換する
  @return string
  """
  return getRunCd(file).split('\\')[-1]

def fullPath(*path):
  """
  相対パスから絶対パスに変換する
  @param * string path
  @return string[]
  """
  return os.path.abspath(os.path.join(os.getcwd(), *path))

def fullPathUpdate(dic):
  """
  辞書型の値のパスを相対パスから絶対パスに変換する (だいぶ無理くり感あるw)
  @param [T, string] dic
  """
  temp = {}
  for k, v in dic.iteritems():
    temp[k] = fullPath(v)
  dic.update(temp) 

def runCommand(*args):
  """
  コマンドを実行する (複数の引数を渡すと自動的に空白切りになる)
  ※ 実行確認用にprintで表示されます
  @param * string args 実行する命令と引数
  @return int コマンドのエラーコード 0以外だとエラーが発生している
  @example runCommand("echo", "Hello World")
  @example runCommand("xxx.exe", "-h")
  """
  message = ' '.join(args)
  log("command " + message)
  process = subprocess.Popen(message, shell=True)
  ret = process.wait()
  return ret

# get absolute directory
def getDir(path):
  """
  指定したパス内に存在するディレクトリを取得する
  @param string path
  @return string[]
  """
  files = os.listdir(fullPath(path))
  return [fullPath(path, file) for file in files if os.path.isdir(fullPath(path, file))]

def getCdRelative():
  """
  フルパスのカレントディレクトリ名から現在のディレクトリのみに変換する
  @return string
  """
  return os.getcwd().split('\\')[-1]

def fileName(path):
  """
  フルパス名からファイル名を取得する
  @param string path
  @return string
  """
  return os.path.basename(path)

def fileNameWithoutExtension(path):
  """
  フルパス名から拡張子なしのファイル名を取得する
  @param string path
  @return string
  """
  file, ext = os.path.splitext(os.path.basename(path))
  return file

def isEmpty(str):
  """
  文字列が空かどうか確かめる
  @param string str
  @return bool
  """
  return len(str) == 0

def findFiles(dir, wildcard=""):
  """
  ディレクトリからファイルを取得する
  @param string dir
  @param string wilecard 正規表現
  @return string[]
  """
  if isEmpty(wildcard):
    return glob.glob(dir)
  return glob.glob(join(dir, wildcard))

def readFile(path):
  """
  ファイルを読み込む
  @param string path
  @return string ファイルデータ
  """
  with open(path) as file:
    return file.read()
  
def readFileLines(path):
  """
  ファイルを読み込む 
  @link https://www.quark.kj.yamagata-u.ac.jp/~hiroki/python/?id=4
  @param string path
  @return string[] 文字配列
  """
  with open(path) as file:
    return file.read().strip().split("\n")

def writeFile(path, message, mode = "w"):
  """
  ファイルにメッセージを書き込む
  @param string path
  @param string message
  @param string mode 新規、上書きの指定
  """
  with open(path, mode) as file:
    file.write(message)

def writeList(path, file_list, mode = "w"):
  """
  ファイルにリストを書き込む
  @param string path
  @param string[] file_list
  @param string mode 新規、上書きの指定
  """
  with open(path, mode) as file:
    for v in file_list:
      v = fileName(v)
      file.write(v + "\n")

def cleanup(path):
  """
  特定または複数のファイル削除する (正規表現)
  @param string path
  """
  files = glob.glob(path);
  for file in files:
    os.remove(file)

def remove(path):
  """
  ファイルを削除する (パスが存在しない場合なにもしない)
  @param string path
  """
  if pathExist(path):
    os.remove(path)

def copy(path, dstDir):
  """
  pathをdstDirにコピーする
  既に存在する場合は削除してからコピーする
  @param string file
  @param string dstDir
  """
  dst = join(dstDir, fileName(path))
  # if pathExist(dst):
  #   if os.path.isfile(dst):
  #     remove(dst)
  #   elif os.path.isdir(dst):
  #     rmDir(dst)
  shutil.copyfile(path, dst)
  log("copy {0} > {1}".format(path, dst))

def copyDir(srcDir, dstDir):
  """
  ディレクトリをコピーする
  ※ dstDirが存在する場合、最初に削除する
  @param string srcDir
  @param string dstDir
  """
  rmDir(dstDir)
  shutil.copytree(srcDir, dstDir)
  log("copyDir {0} > {1}".format(srcDir, dstDir))

def copyFiles(path, dstDir):
  """
  正規表現を使い、複数ファイルを取得しdstDirにコピーする
  @param string path (正規表現あり)
  @param string dstDir
  """
  files = glob.glob(path);
  for file in files:
    dstFile = join(dstDir, fileName(file))
    shutil.copyfile(file, dstFile)
    log("copy {0} > {1}".format(file, dstFile))

def findCdPos(str):
  """
  カレントディレクトリから特定の文字列を検索する その文字列を含めた位置のposを返す
  @param string str
  @return int 失敗したら-1, 成功した場合、検索する文字列を含めた位置
  """
  pos = cd().find(str)
  if pos == -1:
    return '' 
  return cd()[0: pos + len(str) + 1]

def fileCompare(file1, file2):
  """
  2つのファイルを比較する
  @param string file1
  @param string file2
  @return bool 同一の場合 True, そうでない場合 False
  """
  return filecmp.cmp(file1, file2, shallow=False)
