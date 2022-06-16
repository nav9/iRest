This program is under construction.
  
# About iRest  
A program that reminds you to rest your eyes. This program is being created after more than a decade of my experience with chronic eye strain and my eventual recovery. The "i" at the beginning of "iRest" has nothing to do with the Apple company. The "i" refers to you.
  
## iRest was created because...
I (Navin) have spent almost a decade, suffering from chronic eye strain. When new spectacles, eye drops and a lot of the other nonsense didn't cure me, I had to figure out what actually does cure eye strain. The answer was simply to get proper rest, sleep and nutrition. iRest helps with getting proper rest. A key feature is that it is designed to take into account shutdowns, system restarts, lock-screen mode and will perhaps even be designed to use Machine Learning to understand and adapt to our work patterns.   
Many people have created software for taking rest. However, most of them are created with a poor understanding of what actually cures the strain.  
More information here: https://nrecursions.blogspot.com/2020/11/the-real-cure-for-eye-strain.html
  

# IDE used  
VS Code. You'll notice some extra files like launch.json that are located in the `.vscode` folder. Such files are specific to VS Code. These files and the IDE are not essential to running the program. You can simply run the program from the commandline using `python3 main.py`.
  

# Supporting programs required to run iRest 
* Python==3.3   
* For configurations: `pip install dynaconf==3.1.9` (not yet used in the program)  
* To sort filenames with numbers correctly: `pip install natsort==8.1.0`  
* For graphical notification displays (crossplatform): `pip install plyer==2.0.0`
* For playing sound files (crossplatform): `pip install ffmpeg-python==0.2.0 pydub==0.25.1`
  
## On Linux (Ubuntu 16.04)  
* Gnome screensaver (to detect when the screen is locked): `sudo apt install -y gnome-screensaver`.
* Speech Dispatcher engine (for spoken audio notifications. This would be pre-installed on Ubuntu). If it isn't already installed, you can install it using: `sudo apt-get install speech-dispatcher` (https://command-not-found.com/spd-say).
  
  
# To run test cases (yet to be programmed)  
Install PyTest: `pip install pytest==7.1.2`  
  
  
# Attribution  
* Sound files are from https://notificationsounds.com
* I created the icon files. I'm providing them under the Creative Commons Attribution 4.0 International Public License: https://creativecommons.org/licenses/by/4.0/legalcode


