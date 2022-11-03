This program is under construction.
  
# About iRest  
A program that reminds you to rest your eyes. This program is being created after more than a decade of my experience with chronic eye strain and my eventual recovery. The "i" at the beginning of "iRest" has nothing to do with the Apple company. The "i" refers to you, when you use the program.
  
# To run the program  
`python main.py`  
  
## To run from Ubuntu's startup applications  
In this case, the time files and log files will be created in Ubuntu's home folder. It's helpful to redirect stdout in this manner to be able to see the reason for any crashes.    
Use this line in the "command" field: `python -B /path/to/iRest/main.py >> iRestErrors.log`. The `-B` flag is to prevent Python from generating the `__pycache__` folder and `.pyc` bytecode files.  
If the application to run startup apps is missing in your newer version of Ubuntu, simply install it: `sudo apt-get install gnome-startup-applications`.  
  
## iRest was created because...
I (the program creator) have spent almost a decade, suffering from chronic eye strain. When new spectacles, eye drops and a lot of the other nonsense didn't cure me, I had to figure out what actually does cure eye strain. The answer was simply to get proper rest, sleep and nutrition. iRest helps with getting proper rest. A key feature is that it is designed to take into account shutdowns, system restarts, lock-screen mode and will perhaps even be designed to use Machine Learning to understand and adapt to the User's work patterns.   
Many people have created software for taking rest. However, most of them are created with a poor understanding of what actually cures the strain.  
More information here: https://nrecursions.blogspot.com/2020/11/the-real-cure-for-eye-strain.html  
  

# IDE used  
VS Code. You'll notice some extra files like launch.json that are located in the `.vscode` folder. Such files are specific to VS Code. These files and the IDE are not essential to running the program. You can simply run the program from the commandline using commands mentioned above.
  

# Supporting programs required to run iRest  
These could have been mentioned in a `requirements.txt` file, but is mentioned as such to not have to constantly go through the extra steps of keeping the `readme` explanations and `requirements.txt` file synchronized.
* Python version 3.3+ (in this case, version 3.9.6). It is recommended that you install Python either using PyEnv or Anaconda/Miniconda.     
* `pip install natsort==8.1.0`: To sort filenames with numbers correctly.  
* `pip install plyer==2.0.0`: For graphical notification displays (supposed to be crossplatform).
* `pip install ffmpeg-python==0.2.0 pydub==0.25.1`: For playing sound files (supposed to be crossplatform).
* `pip install PySimpleGUI=4.60.3`: For a GUI control panel (supposed to be crossplatform).   
* `pip install dynaconf==3.1.9` (not yet used in the program): For configurations.  
  
## On Linux (Ubuntu 16.04)  
* `sudo apt install -y gnome-screensaver`: Gnome screensaver (to detect when the screen is locked).
* `sudo apt-get install speech-dispatcher`: Speech Dispatcher engine (for spoken audio notifications. This would be pre-installed on Ubuntu). If it isn't already installed, you can install it using (https://command-not-found.com/spd-say).
  
## On Windows and Mac  
Not yet tested.
  
# To run test cases (yet to be programmed)  
Install PyTest: `pip install pytest==7.1.2`  
   
  
# Attribution  
* Sound files are from https://notificationsounds.com (not yet used).  
* I created the icon files myself (not yet used). I'm making them available under the Creative Commons Attribution 4.0 International Public License: https://creativecommons.org/licenses/by/4.0/legalcode  
  
# TODO
* Reduce the strain rate value when watching a video. Program needs to detect the active window (https://stackoverflow.com/questions/52545937/how-can-i-list-all-open-x11-windows-on-gnu-linux-from-a-python-script, https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window, https://stackoverflow.com/questions/5262413/does-xlib-have-an-active-window-event). This could also be programmed with a computer vision algorithm, to check if the video is being played on YouTube.
* Start iRest as a GUI using PySimpleGUI. This would make it easier to pause the program and to view metrics.
* Adding test cases.
