## safety-razer

Ever accidentally run a command as `root`? 

`safety-razer` helps keep you aware of when you're logged in as `root` by setting every connected `Razer` device's lighting effect to a deep red. When you run a command as a non-root user, it will set the lighting effect to a calm blue. 

### Installation

1. First, install `OpenRazer` by following the instructions at the bottom of [this page](https://openrazer.github.io).
2. Clone this repository, install the dependencies, and add the script to your `~/.zshrc` or `~/.bashrc` to be run on login.

```zsh
$ git clone https://github.com/alichtman/safety-razer
$ cd safety-razer
$ pip3 install -r requirements.txt
$ echo "sudo python3 safety-razer.py &" >> ~/.zshrc
```

### Future Development

If there are drivers for other RGB-enabled keyboards available, I'd like to add them. I happen to have only a `Razer` keyboard, and that's the reason this project is currently limited to Razer keyboards.

### Notes

This project is under development. If you run into any issues using it, please open an issue [here](https://github.com/alichtman/safety-razer/issues/new).

It is licensed under GPL v3 and is not officially endorsed by [`Razer`](https://www.razer.com).
