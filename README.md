# pyGitSync
Реализация GitSync (https://github.com/oscript-library/gitsync с вкл. плагином edtExport) на Python.
 ## Краткое описание
 ### Введение
 Данный скрипт, аналогично всем известному GitSync, выгружает из хранилища 1С файлы конфигурации в формате 1С, затем преобразовывает их в формат EDT и помещает в локальную папку, которая находится под контролем GIT. Отличием его от GitSync, является то, что он:
- не ищет папку src, чтобы в нее выгрузить все файлы EDT, создав вложенность папок;
- (если решить первое путем закоменчивания соответвующего куска кода https://github.com/khorevaa/gitsync-plugins/issues/53 )не очищает целевой каталог полностью, а только те каталоги и файлы, которые выгружаются при конвертировании(. settings DT-INF SRC .project ConfigDumpInfo.xml), тем самым оставляя на месте прочие файлы, которые были помещены хранилище в ручную, например: каталог с настройкой проверки SONARQUBE, Jenkinsfile и т.д..
 > Писался новичком в программировании, прошу сильно не ругать
 ### Синтаксис команды
     python pyGitSync_Develop.py -storage=%storage% -gitdir=%gitdir% -version1c=%version1c% -edtVersion=2021.10.5 -tempdir=%tempdir% -projectname=%projectname% -commit=%commit% -storlogin=%storlogin% -storpasswd=%storpasswd%
#### Параметры:
- storage - папка с хранилищем конфигурации 1С
- gitdir - папка GIT
- version1c - версия 1С. подставится в путь c:\program files\1cv8\<version>\bin\1cv8.exe
- edtVersion - версия EDT. 
- tempdir - папка для временных файлов
- projectname - имя проекта
- commit - НЕ РЕАЛИЗОВАНО, но ставить обязательно
- storlogin - пользователь с доступом к хранилищу
- storpasswd - пароль
#### Пример запуска в Windows
```
echo off
chcp 65001
set storage=c:\REPOS_1C\hotfix
set gitdir=C:\REPOS_GIT\hotfix
set version1c=8.3.18.1483
set edtVersion=2021.10.5
set tempdir=c:\temp\_1
set projectname=zup_10229
set commit=True
set storlogin=USERNAME
set storpasswd=PASSWORD

python pyGitSync.py -storage=%storage% -gitdir=%gitdir% -version1c=%version1c% -edtVersion=%edtVersion% -tempdir=%tempdir% -projectname=%projectname% -commit=%commit% -storlogin=%storlogin% -storpasswd=%storpasswd%
```
### Важно
В корне локального каталога git, должны быть расположены два файла: AUTHORS - содержит имена пользователей, логин и email (требуются для commit) и VERSION - формат XML, хранит актуальную зафиксированную версию в GIT-е. НЕ PUSH. А Commit !!!
не нужно наверное говорить, что должен быть установлено ПО: 1С, EDT
##### Пример AUTHORS
```    
ИвановИИ=rivanov_ii <ivanov@domain.ru>	
ПетровПП=Petrov <t.adamov@domain.ru>	
СидоровСС=S.Sidorov <sidor@localhost>	
```
##### Пример VERSION
```
<?xml version="1.0" encoding="UTF-8"?>
<VERSION>145</VERSION>
```
##### Пример каталога GIT
<img width="316" alt="Screenshot_44" src="https://user-images.githubusercontent.com/54239128/146241515-53f5cf48-a571-4a48-8301-f94da91a8707.png">
