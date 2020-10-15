A plugin for openbullet

To Use: run pyinstaller on the installme.py script inside of the repo. The file will be large and may take some time

After that put the compiled exe into your openbullet folders root dir

Use the shell plugin (from ruri) provided in the repo to pass the arguments needed to the program.

Make sure your OB directory has chromedriver.exe and yolov3.weights inside of it along side the compiled script.

example (Loli Script):
SHELL "hcap.exe" "caspers.app eaaffc67-ea9f-4844-9740-9eefd238c7dc" -> VAR "Hcap" 

PARSE "<Hcap>" LR "[KEY] UUID:" "" CreateEmpty=FALSE -> CAP "HcapKey" 
  
Thats all.
