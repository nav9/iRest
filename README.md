This program is under construction, but can still be used.    
  
![Alt text](gallery/iRest_GUI.png?raw=true "The iRest GUI") 

# About iRest  
A program that reminds you to rest your eyes. This program is being created after more than a decade of my experience with chronic eye strain and my eventual recovery. There are many break reminder software. What sets iRest apart from the others is its ability to keep track of strained time even if the computer is restarted or suspended. Additionally, since program activity is logged, it is easier to perform analytics on the log files (with a small margin of error).  
The "i" at the beginning of "iRest" has nothing to do with the Apple company. The "i" refers to you, when you use the program.
  
# To run the program  
First install the required packages:  
`pip install -r requirements.txt`  
Then run the program.  
`python main.py`  
  
## To run it from Ubuntu's startup applications  
In this case, the time files and log files will be created in Ubuntu's home folder. It's helpful to redirect stdout in this manner to be able to see the reason for any crashes.    
Use this line in the "command" field: `python -B /path/to/iRest/main.py >> iRestErrors.log`. The `-B` flag is to prevent Python from generating the `__pycache__` folder and `.pyc` bytecode files.  
If the application to run startup apps is missing in your newer version of Ubuntu, simply install it: `sudo apt-get install gnome-startup-applications`.  
  
## To run it from Mint Cinnamon     
I had to create a file named `startupScript.sh` in the home folder, then run `chmod +x startupScript.sh` to make the script executable. Contents of the file would typically be like (you'll need to set the correct python bin folder for you):  
```
#!/usr/bin/env bash
cd /home/<username>/iRest/
/home/<username>/.pyenv/versions/3.9.0/bin/python3.9 -B /home/nav/iRest/main.py >> iRestErrors.log &
```
  
## iRest was created because...
I (the program creator) have spent almost a decade, suffering from chronic eye strain. When new spectacles, eye drops and a lot of the other nonsense didn't cure me, I had to figure out what actually does cure eye strain. The answer was simply to get proper rest, sleep and nutrition. iRest helps with getting proper rest. A key feature is that it is designed to take into account shutdowns, system restarts, lock-screen mode and will perhaps even be designed to use Machine Learning to understand and adapt to the User's work patterns.   
Many people have created software for taking rest. However, most of them are created with a poor understanding of what actually cures the strain.  
More information here: https://nav9.medium.com/the-real-cure-for-eye-strain-6483490d150f  
  

# IDE used  
VS Code. You'll notice some extra files like `launch.json` that are located in the `.vscode` folder. Such files are specific to VS Code. These files and the IDE are not essential to running the program. You can simply run the program from the commandline using commands mentioned above.
  

# Supporting programs required to run iRest  
These are mentioned in a `requirements.txt` file, but is mentioned as such to not have to constantly go through the extra steps of keeping the `readme` explanations and `requirements.txt` file synchronized.  
* Python version 3.3+ (in this case, version 3.9.0). It is recommended that you install Python either using PyEnv or Anaconda/Miniconda.     
* natsort: To sort filenames with numbers correctly.  
* plyer: For graphical notification displays (supposed to be crossplatform).  
* ffmpeg-python and pydub: For playing sound files (supposed to be crossplatform).  
* PySimpleGUI: For a GUI control panel (supposed to be crossplatform).   
* ConfigParser: For configuration store.  
    
## On Linux 
Based on which desktop the Linux OS uses, the screensaver or lock screen function may vary, so the appropriate program needs to be installed and the necessary changes need to be made in the code.
  
### Also install:  
* `sudo apt-get install speech-dispatcher`: Speech Dispatcher engine (for spoken audio notifications. This would be pre-installed on Ubuntu). If it isn't already installed, you can install it using https://command-not-found.com/spd-say. 

### Ubuntu 20.04 onward  
* `sudo apt install -y gnome-screensaver`: Gnome screensaver (to detect when the screen is locked).  
* Ubuntu has a native colour temperature app. If you don't want to use that, install `sudo apt install -y sct`, and colour temperature adjustment will automatically show up on iRest's GUI.

### Mint OS 21 onward (Cinnamon desktop)  
* `sudo apt install -y sct`: Set screen colour temperature (to set the screen to warmer colours).  

### Some helpful aliases for iRest
You can place these aliases in `~/.bash_aliases`:
* `alias killirest="kill -9 $(pgrep -f 'iRest')"`
* `alias pauseirest="kill -STOP $(pgrep -f 'iRest')"`
* `alias resumeirest="kill -CONT $(pgrep -f 'iRest')"`
* `alias ireststatus="ps -aef | grep iRest"`
* `alias irest="cd ~;cd /path/to/iRest/folder/;python -B /path/to/iRest/folder/main.py >> iRestErrors.log"`
* `alias restartirest="killirest; irest"`
  
## On Windows (8.1)   
* Install Python 3.6+ and add Python to the PATH variable during installation itself (you'll be shown a checkbox).  
* Download `ffmpeg` and add the path to ffmpeg's bin folder to the System PATH variable.  
* `pip install natsort plyer ffmpeg-python pydub`  
* Add iRest to Windows startup by pressing `Win+R` and type `shell:startup`. You'll be taken to the `C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup` folder. Here, create an `irest.bat` file containing the lines `cd C:\Users\<username>\Desktop\iRest-main\` and `python main.py` in the next line.  
  
# To run the tests  
It's not necessary to use the exact version of pytest mentioned below. The version is mentioned only to indicate which version was used at the time.  
`pip3 install pytest=7.1.2`    
Use `pytest` at the commandline to run the test cases. Do this in the root program directory.  
To run `pytest` for a specific test file only, run it like this: `pytest tests/test_filename.py`.  
To run `pytest` for a specific test function in a test file, run it like this: `pytest tests/test_filename.py -k 'test_functionName'`.  
To see the captured output of passed tests, use `pytest -rP`. For failed tests, use `pytest -rx`. All outputs will be shown with `pytest -rA`.  
  
# Attribution  
* Sound files are from https://notificationsounds.com (not yet used).  
* I created the icon files myself (not yet used). I'm making them available under the Creative Commons Attribution 4.0 International Public License: https://creativecommons.org/licenses/by/4.0/legalcode  
  
# TODO
* Create a script for each OS, which will automatically install necessary apps and packages.  
* Track and show how much time the program has been under pause.
* Have a config file that stores program settings.
* Reduce the strain rate value when watching a video. Program needs to detect the active window (https://stackoverflow.com/questions/52545937/how-can-i-list-all-open-x11-windows-on-gnu-linux-from-a-python-script, https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window, https://stackoverflow.com/questions/5262413/does-xlib-have-an-active-window-event). This could also be programmed with a computer vision algorithm, to check if the video is being played on YouTube.
* View metrics of time strained.
* Adding test cases.
