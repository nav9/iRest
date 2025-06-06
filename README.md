This program is under construction (and the documentation a bit messy), but iRest can still be used. If you'd like to contribute to this project, please let me know.    
  
![Alt text](gallery/iRest_GUI.png?raw=true "The iRest GUI") 

# About iRest  
Created by the author of [The Real Cure for Eye Strain](https://nav9.medium.com/the-real-cure-for-eye-strain-6483490d150f), iRest is a program that reminds you to rest your eyes. A major feature being that it keeps track of the accumulated strain even if you restart the computer or iRest and even if you suspend the computer.  
There is much more to be programmed and to be made configurable on various operating systems.   
Since program activity is logged, it is easier to perform analytics on the log files (with a small margin of error).  
The "i" at the beginning of "iRest" refers to you, and has nothing to do with the Apple company.   
**Remember: iRest is programmed to automatically minimise its GUI when it starts.**  
  
## iRest was created because...
Many people have created software that remind them to take rest. However, most of them are created with a poor understanding of what actually cures eye 
strain, and almost all of them don't keep track of strained time between restarts/shutdowns, so you end up getting strained more. 
This may seem trivial, but is critical for people suffering chronic strain.    
* **The 20-20-20 rule is wrong:** The creator of the rule himself said so when asked. Yet some eye rest software and doctors emphasize 20-20-20. The right way to get rest is to keep the eyes closed for around 5 minutes (or until the strain subsides) after every 20 minutes of strain.  
* **Eye exercises are wrong:** Tired eye muscles need rest, and not exercise. Yet many eye rest software incorrectly recommend eye exercises.   
I have suffered chronic eye strain for almost a decade. When new spectacles, eye drops and a lot of the other nonsense 
did not cure me, I had to figure out what actually does cure eye strain. The answer was simply to get proper rest, sleep and nutrition. 
iRest helps with getting proper rest. A key feature is that it is designed to take into account shutdowns, system restarts, lock-screen mode 
and may perhaps even be designed to use Machine Learning to understand and adapt to the User's work patterns and User-communicated sleep sufficiency.   
      
# To run iRest on Linux 
First install the required packages:  
`chmod +x install_on_linux.sh;./install_on_linux.sh`  
Then run the program.  
`python main.py`  
Based on which desktop the Linux OS uses, the screensaver or lock screen function may vary, so the appropriate program needs to be installed and the necessary changes need to be made in the code.  

## Nuances for Ubuntu
In this case, the time files and log files will be created in Ubuntu's home folder. It's helpful to redirect stdout in this manner to be able to see the reason for any crashes.    
Use this line in the "command" field: `python -B /path/to/iRest/main.py >> iRestErrors.log`. The `-B` flag is to prevent Python from generating the `__pycache__` folder and `.pyc` bytecode files.  
If the application to run startup apps is missing in your newer version of Ubuntu, simply install it: `sudo apt-get install gnome-startup-applications`.  
* Install `sudo apt-get install speech-dispatcher`: Speech Dispatcher engine (for spoken audio notifications. This would be pre-installed on Ubuntu). If it isn't already installed, you can install it using https://command-not-found.com/spd-say. 
  
### Ubuntu 20.04 onward  
* `sudo apt install -y gnome-screensaver`: Gnome screensaver (to detect when the screen is locked).  
* Ubuntu has a native colour temperature app. If you don't want to use that, install `sudo apt install -y sct`, and colour temperature adjustment will automatically show up on iRest's GUI.  
  
## Nuances for Mint Cinnamon     
I had to create a file named `startupScript.sh` in the home folder, then run `chmod +x startupScript.sh` to make the script executable. Contents of the file would typically be like (you'll need to set the correct python bin folder for you):  
```
#!/usr/bin/env bash
cd /home/<username>/iRest/
/home/<username>/.pyenv/versions/3.9.0/bin/python3.9 -B /home/<username>/iRest/main.py >> iRestErrors.log &
```
### Mint OS 21 onward (Cinnamon desktop)  
* `sudo apt install -y sct`: Set screen colour temperature (to set the screen to warmer colours).  
   
# To run iRest on Raspberry Pi
Install necessary packages using the `install_on_RaspberryPi.sh` script.  
`chmod +x install_on_RaspberryPi.sh;./install_on_RaspberryPi.sh`  
Follow the instructions at the end of the script to enable detection of screen lock.  
Oddly, iRest did not work when run with `crontab` or `systemd` or `.profile`. So the only option was to put it in `.bashrc` and open a terminal to start iRest. There may be [other ways](https://unix.stackexchange.com/a/317659).  
 
# To run iRest on Windows
I don't use Windows anymore so I didn't really bother.   
## On Windows (8.1)   
* Install Python 3.6+ and add Python to the PATH variable during installation itself (you'll be shown a checkbox).  
* Download `ffmpeg` and add the path to ffmpeg's bin folder to the System PATH variable.  
* `pip install natsort plyer ffmpeg-python pydub`  
* Add iRest to Windows startup by pressing `Win+R` and type `shell:startup`. You'll be taken to the `C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup` folder. Here, create an `irest.bat` file containing the lines `cd C:\Users\<username>\Desktop\iRest-main\` and `python main.py` in the next line.    
   
# IDE used  
VS Code (on Raspberry pi you can use Geany). You'll notice some extra files like `launch.json` that are located in the `.vscode` folder. Such files are specific to VS Code. These files and the IDE are not essential to running the program. You can simply run the program from the commandline using commands mentioned above.

### Some helpful aliases for iRest
You can place these aliases in `~/.bash_aliases`:
* `alias killirest="kill -9 $(pgrep -f 'iRest')"`
* `alias pauseirest="kill -STOP $(pgrep -f 'iRest')"`
* `alias resumeirest="kill -CONT $(pgrep -f 'iRest')"`
* `alias ireststatus="ps -aef | grep iRest"`
* `alias irest="cd ~;cd /path/to/iRest/folder/;python -B /path/to/iRest/folder/main.py >> iRestErrors.log"`
* `alias restartirest="killirest; irest"`
  
# To run the tests  
It's not necessary to use the exact version of pytest mentioned below. The version is mentioned only to indicate which version was used at the time.  
`pip3 install pytest=7.1.2`    
Use `pytest` at the commandline to run the test cases. Do this in the root program directory.  
To run `pytest` for a specific test file only, run it like this: `pytest tests/test_filename.py`.  
To run `pytest` for a specific test function in a test file, run it like this: `pytest tests/test_filename.py -k 'test_functionName'`.  
To see the captured output of passed tests, use `pytest -rP`. For failed tests, use `pytest -rx`. All outputs will be shown with `pytest -rA`.  
  
# Attribution  
* Sound files are from https://notificationsounds.com (not yet used).  
* I created the icon files myself. I'm making them available under the Creative Commons Attribution 4.0 International Public License: https://creativecommons.org/licenses/by/4.0/legalcode  
  
# TODO
* Use espeak across Linux and have an option for iRest to detect which speech program is installed and use that.  
* Create a script for each OS, which will automatically install necessary apps and packages.  
* Track and show how much time the program has been under pause.  
* Have a config file that stores program settings and be able to edit it from the GUI.  
* Reduce the strain rate value when watching a video. Program needs to detect the active window (https://stackoverflow.com/questions/52545937/how-can-i-list-all-open-x11-windows-on-gnu-linux-from-a-python-script, https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window, https://stackoverflow.com/questions/5262413/does-xlib-have-an-active-window-event). This could also be programmed with a computer vision algorithm, to check if the video is being played on YouTube.  
* View metrics of time strained.  
* Adding more test cases.  
  
[![Donate](https://raw.githubusercontent.com/nav9/VCF_contacts_merger/main/gallery/thankYouDonateButton.png)](https://nrecursions.blogspot.com/2020/08/saying-thank-you.html)      
