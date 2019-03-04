## safety-razer

Ever accidentally run a command as `root`? 

`safety-razer` helps keep you aware of when you're logged in as `root` by setting every connected Razer device's lighting effect to a deep red. When you run a command as a non-root user, it will set the lighting effect to a calm blue. 

### Installation

**Notes**

+ An `OpenRazer` supported Linux distribution is needed.
+ `zsh` must be installed.

1. First, install `OpenRazer` by following the instructions at the bottom of [this page](https://openrazer.github.io). For this demo, I've decided to use `OpenSUSE`.

2. Clone this repository, install the dependencies, and add the script to your `~/.zshrc` to be run on login.

```zsh
$ git clone https://github.com/alichtman/safety-razer
$ cd safety-razer
$ pip3 install -r requirements.txt
$ echo "sudo python3 safety-razer.py &" >> ~/.zshrc
```

