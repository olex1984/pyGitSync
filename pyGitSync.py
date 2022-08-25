import collections
from datetime import datetime as dt
import string
import os
import sys
import logging
import datetime
import argparse
from sys import path, platform, stderr, stdout
import uuid
import subprocess
import time
import shutil
import xml.etree.ElementTree as ET

### python cf_actual_checker.py -days=30 -files_dir="C:\release_cf" -cmd=delete -filter=cf
class argument():
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(description='O_O')
        my_namespace = self.parse_args(parser)
        self.storage = str(my_namespace.storage)
        self.gitdir = str(my_namespace.gitdir)
        self.version1c = str(my_namespace.version1c)
        self.tempdir = str(my_namespace.tempdir)
        self.projectname = str(my_namespace.projectname)
        self.commit = str(my_namespace.commit)
        # self.ext_name = str(my_namespace.ext_name) #Используется только вов нешних.
        self.storlogin = str(my_namespace.storlogin)
        self.storpasswd = str(my_namespace.storpasswd)
        self.edtVersion = str(my_namespace.edtVersion)

    def parse_args(self, parser):
        for n in sys.argv[1:]:
            parser.add_argument(self.split(n)) 
        my_namespace = parser.parse_args()
        return my_namespace      
    
    def split(self, val):
        arg_key = str(val).split("=")
        return str(arg_key[0]) 

def isWindows() -> bool:
    if platform == "linux" or platform == "linux2":
        return False
    elif platform == "darwin":
        return False
    elif platform == "win32":
        return True

def rightPath(path) -> str:
    lPath = str(path)
    if isWindows():
        lPath = lPath.replace("/","\\")
    elif not isWindows():
        lPath = lPath.os.replace("\\",'/') 
    return lPath

def log(text=None, verbose = True) -> None:
    data = dt.now().strftime("%Y.%m.%d %H:%M:%S")
    if bool(verbose):
        print(str(data)+" : "+ str(text))

def runCMD(command) -> None:
    try:
        log("Params: "+command)
        result = subprocess.run(["cmd.exe", "/C", str(command).strip()], encoding="utf-8", text=True)
        returnCode = result.returncode
        log("Return Code = "+str(returnCode))
        if int(returnCode) > 0:
            log("Ошибка в процессе выполнения.")
            exit(1)
        else:
            log("Успешно.")
    except Exception as e:
        log(e)
        exit(1)

def runCommand(program, params = None, outFile = None) -> None:
    try:
        if not params is None:
            log("RUN: "+program)
            log("Params: "+ params)
            result = subprocess.run([program,params],encoding="utf-8", text=True)
        elif params is None:
            log("RUN: "+program)
            result = subprocess.run(program, encoding="utf-8", text=True)
        returnCode = result.returncode
        log("Return Code = "+str(returnCode))
        if int(returnCode)>0:
            log("Ошибка в процессе выполнения.")
            if not outFile is None:
                f= open(outTxt,mode="r",encoding="utf-8-sig")
                text = f.read()
                f.close()
                log("_LOGFILE_: "+text)
            exit(1)
        else:
            log("Успешно")
            if not outFile is None:
                f= open(outTxt,mode="r",encoding="utf-8-sig")
                text = f.read()
                f.close()
                log("_LOGFILE_: "+text)
    except Exception as e:
        log(e)
        exit(1)

def getUid(string_length=5) -> string:
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    #random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.

def prepareNextBuild(temp_path, folderList ) -> None:
    if os.path.exists(temp_path):
        for item in folderList:
            try:
                obj = os.path.join(temp_path,item)
                log("Очистка:"+obj)
                if os.path.isfile(obj):
                    os.remove(obj)
                elif os.path.isdir(obj):
                    shutil.rmtree(obj)
            except Exception as e:
                log(e)
                exit(1)

def checkTempDir(temp_path, delete=False) ->None:
    if os.path.exists(temp_path):
        log("Вреемнный каталог существует. Очистка от мусора.")
        try:
            res = deletePath(temp_path)
            if res > 0:
                exit(1)
            time.sleep(2)
            os.makedirs(temp_path)
        except:
            log("Удаление временного каталога: FAILED. Check permissions.")
            exit(1)  
    else:
        try:
            log("Создание временного каталога.")
            os.makedirs(temp_path)
        except:
            log("Создание временного каталога: FAILED. Check permissions.")
            exit(1)

def getVersionNumber(versionFile) -> str:
    tree = ET.parse(versionFile)
    root = tree.getroot()
    log("Версия в GIT:")
    log("<VERSION>"+str(root.text)+"</VERSION>")
    return str(root.text)

def getDictTemplate() -> dict:
    lDict = {}
    lDict["Версия"]=""
    lDict["Версия конфигурации"]=""
    lDict["Пользователь"]=""
    lDict["Дата создания"]=""
    lDict["Время создания"]=""
    lDict["Метка"]=""
    lDict["Комментарий"]=""
    return lDict

def parseReport4Array(file) -> list:
    ldict = None
    text = []
    commits = []
    with open(file, 'r',encoding="utf-8-sig") as f:
        for line in f:
            if len(str.strip(line)) > 1:
                text.append(line)
        text.append("EOF")
    comment = False
    for line in text:
        if str.find(str(line).strip(),":") >=0:
            l = []
            splitLine = str.split(line,":",1)
            for i in splitLine:
                l.append(str.strip(i))
            
            if l[0] == "Версия":
                if comment:
                    commits.append(ldict)
                    ldict = None
                comment = False
                ldict = getDictTemplate()
                ldict[l[0]]=l[1]
                log(l[0]+":"+l[1])
            elif l[0] == "Версия конфигурации":
                ldict[l[0]]=l[1]
                log(l[0]+":"+l[1])
            elif l[0] == "Пользователь":
                ldict[l[0]]=l[1]
                log(l[0]+":"+l[1])
            elif l[0] == "Дата создания":
                ldict[l[0]]=l[1]
                log(l[0]+":"+l[1])
            elif l[0] == "Время создания":
                ldict[l[0]]=l[1]
                log(l[0]+":"+l[1])
                # ++ переход на новую платформу 8.3.21.1302. В ней изменен вывод hil файла. Убрать если версия ниже 8.3.18 (может и между ними где-то сменилось) 
                comment = True
                # -- переход на новую платформу. Изменен вывод hil файла
            elif l[0] == "Метка":
                ldict[l[0]] = l[1]
                log(l[0]+":"+l[1])
            elif l[0] == "Комментарий":
                log(l[0]+":"+l[1])
                comment = True
                try:
                    ldict["Комментарий"]=str(l[1]).strip()
                except:
                    ldict["Комментарий"]=""
            else:
                if comment:
                   ldict["Комментарий"]=ldict["Комментарий"] + str(line)#.strip()#если в етксте программер будет использовать символ ":" в комментарии 
                continue
        
        else:
            if line == "EOF".strip():
                if ldict is not None:
                    commits.append(ldict)
                    ldict = None        
            if comment: #Слово Добавлены, ИЗМЕНЕНЫ вставляет выгрузка 1С в отчет. Она закрывает вовзможность для ввода коментария
                if not (str.find(line, "\tИзменены\t") >= 0 or str.find(line, "\tДобавлены\t") >= 0 or str.find(line, "\tУдалены\t") >= 0):
                    log(line)
                    ldict["Комментарий"]=ldict["Комментарий"] + str(line)#.strip()
                else:
                    comment =False
                    commits.append(ldict)
                    ldict = None
            continue
    
    return commits

def parseAuthors2Dict(file) -> dict:
    employees = []
    with open(file, 'r',encoding="utf-8-sig") as f:
        for line in f:
            employee = {}
            if str.find(line,"=") >=0:
                splitLine = str.split(line,"=",1)
                employee["name"]=str.strip(splitLine[0])
                employee["author"] = str.strip(splitLine[1])
                splitLine[1] = str.replace(splitLine[1],">","")
                loginEmail = str.split(splitLine[1],"<", 1)
                employee["username"] = str.strip(loginEmail[0])
                employee["email"] = str.strip(loginEmail[1])
                employees.append(employee)
    return employees    

def deletePath(path) -> int:
    code = 0
    if os.path.exists(path):
        if os.path.isfile(path) or os.path.islink(path):
            try:
                os.unlink(path)
            except Exception as e:
                log(e)
                code = 1           
        if os.path.isdir(path):
            for elem in os.listdir(path):
                elem_path = os.path.join(path, elem)
                code = deletePath(elem_path)
            try:
                os.rmdir(path)
            except Exception as e:
                code = 1
                log(e)
    else:
        log("Путь: " + path + " не существует. Пропуск ...")
    return code

def moveEdtProjectToGit(srcDir, dstDir, tempDumpDir) -> int:
    ############### TempDumpDir #####################
    configFileName = "ConfigDumpInfo.xml"
    configFilePath = os.path.join(tempDumpDir,configFileName)
    dst_configPath =  os.path.join(dstDir,configFileName)
    if deletePath(dst_configPath) > 0:
        return 1
    log("MOVE \n SRC="+str(configFilePath) +" \nDST="+str(dst_configPath))
    try:
        shutil.move(configFilePath, dst_configPath)
    except Exception as e:
        log(e)
        return 1
    ################ srcDir ##########################
    for item in os.listdir(srcDir):
        dst_path = os.path.join(dstDir,item)
        log("Delete: " + dst_path)
        result = deletePath(dst_path)
        if result > 0:
            return 1
        log("MOVE \n SRC="+str(os.path.join(srcDir,item)) +" \nDST="+str(dst_path))
        try:
            shutil.move(os.path.join(srcDir,item),os.path.join(dstDir,item))
        except Exception as e:
            log(e)
            return 1

    return 0

def generateCommitMessage(dictCommit) -> str:
    data = dt.now().strftime("%Y.%m.%d %H:%M:%S")
    text = str(dictCommit["Комментарий"])
    serviceString = "\nМетка:"+dictCommit["Метка"]+"\nВерсия:"+dictCommit["Версия"]
    commitMessage = ""
    splitText = str(text).splitlines(keepends=True)
    log("Количество строк в комментарии:"+str(len(splitText)))
    if len(splitText) > 1:
        commitMessage = " -m \""+str(splitText[0])+"\""
        splitText.pop(0)
        tmptxt = ""
        for item in splitText:
            tmptxt = tmptxt + item +"\n"

        commitMessage = commitMessage + " -m \""+str(tmptxt)+serviceString+"\""
    else:
        commitMessage = " -m \""+str(text).strip()+serviceString+"\""
    log("Final commit message:"+commitMessage)
    return commitMessage

def saveVersion(versionFile, cur) -> None:
    num = getVersionNumber(versionFile)
    oldNumString = "<VERSION>"+str(num)+"</VERSION>"
    curNumString = "<VERSION>"+str(cur)+"</VERSION>"
    f = open(versionFile, "r+", encoding="utf-8-sig")
    text = f.read()
    f.close()
    text4save = str.replace(text, oldNumString, curNumString)
    log("Запись текущего номера в файл.")
    log(text4save)
    f = open(versionFile, "w", encoding="utf-8-sig")
    f.write(text4save)
    f.close()

def replaceCharactersInCommits(inputCommits) -> list:
    char_to_replace = {'"': '\\\"',
                   '\'': '\\\''}
    outCommits = []
    for commit in inputCommits:
        outDict = {}
        for key, value in commit.items():
            if (key == "Метка" or key == "Комментарий"):
                for keyChar, valueChar in char_to_replace.items():
                    value = value.replace(keyChar, valueChar)
            
            outDict[key] = str(value).strip()
        outCommits.append(outDict)
    
    return outCommits


if __name__ == '__main__':
    log("Запуск конвертации.")
    log("Чтение параметров:")
    try:
        lArgs = argument()
        # print(lArgs.storage)
        # print(lArgs.gitdir)
        # print(lArgs.version1c)
        # print(lArgs.tempdir)
        # print(lArgs.projectname)
        # print(lArgs.commit)
        # print(lArgs.storlogin)
        # print(lArgs.storpasswd)
    except:
        log("Не удалось прочитать все параметры командной строки")
        exit(1)
    versionFileName = "VERSION"
    authorsFileName = "AUTHORS"
    exe1cBin = "bin/1cv8.exe"
    lArgs.gitdir = rightPath(lArgs.gitdir)
    if str.find(lArgs.storage,"tcp://") == -1:
        lArgs.storage = rightPath(lArgs.storage)
    prgm_path = os.environ.get("PROGRAMFILES")
    temp_path = rightPath( lArgs.tempdir)
    tempDBDir = rightPath(os.path.join(temp_path, getUid()))+".DB"
    tempDumpDir = rightPath(os.path.join(temp_path,getUid()))+".DUMP"
    tempWorkspaceLocation = rightPath(os.path.join(temp_path,getUid()))+"_WS"
    tempProjectDir = rightPath(os.path.join(temp_path,getUid()+"_PD",lArgs.projectname))
    repReportFilePath = rightPath(os.path.join(temp_path,getUid()+".txt"))
    exe1cFullPath = rightPath(os.path.join(prgm_path,"1cv8",lArgs.version1c,exe1cBin))
    outTxt = rightPath(os.path.join(temp_path,getUid())) + "_hil.txt"
    versionFilePath = rightPath( os.path.join(lArgs.gitdir, versionFileName))
    authorsFilePath = rightPath(os.path.join(lArgs.gitdir, authorsFileName))
    log("1CPATH: "+exe1cFullPath)
    log("TEMP: "+ temp_path)
    log("TEMPDB_DIR: "+ tempDBDir)
    log("TEMPDUMP_DIR: "+ tempDumpDir)
    log("HIL.TXT: "+ outTxt)

    #--------------------------------------------- STEP 1
    log("Создание временной БД.")
    log("Рабочий каталог: "+os.getcwd())
    checkTempDir(temp_path)
    cmdCreateTempDB = "CREATEINFOBASE File="+tempDBDir+" /Out "+outTxt+" /LRU /VLRU"
    runCommand(exe1cFullPath, cmdCreateTempDB, outTxt)
    
    #--------------------------------------------- STEP 2
    log("Выгрузка отчета по версиям коммитов в хранилище.")
    cmdCreateRepReport = "DESIGNER /F"+tempDBDir+" /Out "+outTxt+" /WA+ /LRU /VLRU /DisableStartupMessages /DisableStartupDialogs /ConfigurationRepositoryN "+lArgs.storlogin+" /ConfigurationRepositoryP "+lArgs.storpasswd+" /ConfigurationRepositoryF "+lArgs.storage+" /ConfigurationRepositoryReport "+repReportFilePath+" -NBegin "+str(int(getVersionNumber(versionFilePath))+1)+" -ReportFormat txt –ReportType Brief -IncludeCommentLinesWithDoubleSlash "
    runCommand(exe1cFullPath,cmdCreateRepReport, outTxt)
    try:
        commits = parseReport4Array(repReportFilePath)
    except Exception as e:
        log(e)
        exit(1)
    commitsCount = len(commits)
      
    if commitsCount > 0:
        log("\nОбнаружены новые коммиты = "+str(commitsCount) +" шт.")
    else:
        log("\nНовых коммитов не обнаружено. Выход.")
        exit(0)
    log(commits)#FIXME
    commitsWOCharacters = replaceCharactersInCommits(commits)
    log(commitsWOCharacters)
    #--------------------------------------------- STEP 3
    log("Загрузка конфигурации из хранилища во временную базу")
    for commit in commitsWOCharacters:
        #------------------------------------------ ЗАГРУЗКА КОНФ. ИЗ ХРАНИЛИЩА в ИБ
        log("\nОбрабатывается коммит №"+commit["Версия"])
        cmdUpdateCFG = "DESIGNER /F"+tempDBDir+" /Out "+outTxt+" /WA+ /LRU /VLRU /DisableStartupMessages /DisableStartupDialogs /ConfigurationRepositoryN "+lArgs.storlogin+" /ConfigurationRepositoryP "+lArgs.storpasswd+" /ConfigurationRepositoryF "+lArgs.storage+" /ConfigurationRepositoryUpdateCfg -v "+commit["Версия"]+" -force "
        runCommand(exe1cFullPath, cmdUpdateCFG)
         
        #------------------------------------------ ВЫГРУЗКА Файлов конфигурации
        log("\nВыгрузка конфигурационных файлов в формате 1С во временную папку.")
        cmdDumpFiles = "DESIGNER /F"+tempDBDir+" /Out "+outTxt+" /WA+ /LRU /VLRU /DisableStartupMessages /DisableStartupDialogs /DumpConfigToFiles "+tempDumpDir+" -format Hierarchical "
        runCommand(exe1cFullPath,cmdDumpFiles)

        #------------------------------------------ Импорт файлов конфигурации в EDT
        log("\nИмпорт конфигурационных файлов во временной хранилище формата EDT ")
        cmdEdtImport = "ring edt@"+lArgs.edtVersion+" workspace import --configuration-files "+tempDumpDir+" --workspace-location "+tempWorkspaceLocation+" --project "+tempProjectDir
        runCMD(cmdEdtImport)

        #------------------------------------------ перенос EDT в локальный гит
        log("\nПеренос хранилища формата EDT в локальную папку GIT "+lArgs.gitdir)
        if moveEdtProjectToGit(tempProjectDir,lArgs.gitdir, tempDumpDir) > 0:
            exit(1)

        os.chdir(lArgs.gitdir)
        #---------- GIT ADD .
        log("\nДобавление файлов для отслеживания GIT.")
        log("Curr workdir:"+os.getcwd())
        cmdGitAddFiles = "git add ."
        runCommand(cmdGitAddFiles)
        
        #----------- GIT COMMIT
        log("\nВыполнение коммита GIT.")
        employees = parseAuthors2Dict(authorsFilePath)
        gitHistoryDate = datetime.datetime.strptime(commit["Дата создания"], '%d.%m.%Y').strftime('%Y-%m-%d')
        gitHistoryDate = gitHistoryDate+"T"+commit["Время создания"]
        commitMessageString = generateCommitMessage(commit)
        for employee in employees:
            if employee["name"] == commit["Пользователь"]:
                log("commitMessageString = "+ commitMessageString)
                data = str(gitHistoryDate).strip()
                log("--date = "+ data)
                lauthor = str(employee["author"]).strip()
                log("--author = "+ lauthor)
                cmdGitCommit = 'git commit '+commitMessageString+' --no-edit --date="'+data+'" --author="'+lauthor+'"'
                log(cmdGitCommit)
        runCommand(cmdGitCommit)
        try:
            log("\nЗапись в файл VERSION")
            saveVersion(versionFilePath, int(commit["Версия"]))
        except Exception as e:
            log(e)
            exit(1)
        
        #-------------------- Удаление временных файлов и папок/ Генерация новых папок для следующей сборки
        tempDumpDir = rightPath(os.path.join(temp_path,getUid()))+".DUMP"
        tempWorkspaceLocation = rightPath(os.path.join(temp_path,getUid()))+"_WS"
        tempProjectDir = rightPath(os.path.join(temp_path,getUid()+"_PD",lArgs.projectname))
        log("Коммит №"+commit["Версия"]+" успешно добавлен в локальное хранилище GIT.")
        #log("\nВсе этапы завершены УСПЕШНО.\n")
        #break #-----------------------UNCOMMENT FOR TEST/DEBUG
log("Чистка после себя темпа.")
checkTempDir(temp_path)    #----------------------- COMMENT FOR TEST/DEBUG
exit(0)