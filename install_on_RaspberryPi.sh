#!/usr/bin/env bash
#sct is for setting warm/nightlight colors. This does not work on Raspberry Pi's wayland desktop
#echo "Installing sct"
#sudo apt install -y sct

#Espeak vocalises words (used to tell the user when to take rest)
echo "Installing espeak."
sudo apt install -y espeak

read -p "Installing Python packages with pip in Raspberry Pi usually ends up in an error so it is advisable to install PyEnv. This script can automatically install version 3.12.10 of Python. Select 'no' if you would prefer to see the script and do the installation yourself. Select 'yes' or 'y' to proceed with automatic installation of pyenv and the pip installs for iRest: Your choice is yes/no? " answer
if [[ "$answer" == "yes" || "$answer" == "y" || "$answer" == "Y" ]]; then
	echo "Proceeding with installing PyEnv"
	curl https://pyenv.run | bash
	#Add environment variables to bashrc
	echo "Adding environment variables to bashrc."
	echo "export PYENV_ROOT='$HOME/.pyenv'" >> ~/.bashrc
	echo "[[ -d $PYENV_ROOT/bin ]] && export PATH='$PYENV_ROOT/bin:$PATH'" >> ~/.bashrc
	echo "eval '$(pyenv init - bash)'" >> ~/.bashrc
	#Restart the terminal to make bashrc changes effective
	exec $SHELL
	#Install other required packages
	echo "Installing other software required for pyenv."
	sudo apt-get install -y libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libgdbm-dev lzma lzma-dev tcl-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev wget curl make build-essential openssl
	pyenv update
	pyenv install --list
	pyenv install 3.12.10
	pyenv global 3.12.10
	echo "Proceeding with installing Python packages from `requirements.txt`"
	pip install -r requirements.txt
else
	echo "Ok then please install PyEnv on your own or whatever solution you have in mind."
	echo "Then run `pip install -r requirements.txt` or look into the `requirements.txt` file to see which pip packages you wish to install at whatever version of the package you choose."
fi


