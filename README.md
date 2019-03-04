## safety-razer

Ever accidentally run a command as `root`? 

`safety-razer` helps keep you aware of when you're logged in as `root` by setting every connected Razer device's lighting effect to a deep red. When you run a command as a non-root user, it will set the lighting effect to a calm blue. 

### Installation

**Notes**

+ An `OpenRazer` supported Linux distribution is needed.
+ `zsh` must be installed.

1. First, install `OpenRazer` by following the instructions at the bottom of [this page](https://openrazer.github.io). For Ubuntu/Linux Mint, the setup is:

```zsh
$ sudo add-apt-repository ppa:openrazer/stable
$ sudo apt update
$ sudo apt install openrazer-meta
```

2. Create a new group called `safety-razer-root` for only you and the new `safety-razer` user we're about to create. Create the new `safety-razer` user, add it to the `sudo` and `safety-razer-root` groups, and set `zsh` as the default shell. Then add your user to the `safety-razer-root` group. *(The reason we're doing this is because it's unsafe to change the default login shell on the `root` account.)*

```zsh
$ sudo groupadd safety-razer-root
$ sudo useradd -s `which zsh` -G sudo,safety-razer-root safety-razer
$ passwd safety-razer # You'll want to password protect this user.
$ sudo usermod -aG safety-razer-root `whoami`
```

3. Set the default shell to zsh, and then log out and log back into your user account.

```zsh
$ chsh -s /bin/bash
$ logout
```

4. Next, set the permissions on your user zsh history file so that everyone in the `user-safety-razer` group can read and write to it. Then, set the zsh history file environment variable for the `safety-razer` user to your user's zsh history file path. Then alias `$ su -`.

```zsh
$ echo $HISTFILE 
$ sudo chgrp safety-razer-root `$HISTFILE`
$ sudo chmod g+wr `$HISTFILE`
$ sudo su safety-razer
$ sudo -H -u safety-razer zsh -c 'export $HISTFILE=<HISTFILE_PATH_THAT_WAS_PRINTED_BEFORE>'
$ echo "alias safety-su"="sudo -i safety-razer" >> ~/.zshrc
```

5. Clone this repository, install the dependencies, and add the script to your `~/.zshrc` to be run on login.

```zsh
$ git clone https://github.com/alichtman/safety-razer
$ cd safety-razer
$ pip3 install -r requirements.txt
$ echo "sudo python3 safety-razer.py &" >> ~/.zshrc
```

