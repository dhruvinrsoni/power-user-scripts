ls=dir $1
alias=doskey $*
a=DOSKEY /MACROS:ALL
e=exit
c=cls
ex    = start .
..    = cd ..\$*
...   = cd ..\..\$*
....  = cd ..\..\..\$*
..... = cd ..\..\..\..\..\$*
...... = cd ..\..\..\..\..\$*

hardhide=attrib +s +h $*
hardshow=attrib -s -h $*

ip=ipconfig 
ipall=ipconfig \all
np=notepad++.exe $*
subl="D:\Sublime Text 3\sublime_text.exe" $*

trainee=explorer "\\10.0.0.48\Trainee"
prez=explorer "D:\Training\presentations"
samples=explorer "D:\Training\samples"
scripts=explorer "D:\Scripts"
network=explorer "\\10.0.0.48\"
opendosfile=notepad "D:\Scripts\doskeys.txt"
cmdtomcat=start cmd /K "cd /d C:\apache-tomcat-9.0.22"
