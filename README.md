## safety-razer

Ever accidentally run a command as `root`? 

`safety-razer` helps keep you aware of when you're logged in as `root` by setting every connected Razer device's lighting effect to a deep red. When you exit from `root`, it will set the lighting effect to a calm blue. 

### Installation

**Note: Requires an OpenRazer supported Linux distribution.**

First, install `OpenRazer` by following the instructions at the bottom of [this page](https://openrazer.github.io).

Then, clone this repository and run the script in the background.

```bash
$ git clone https://github.com/alichtman/safety-razer
$ cd safety-razer
$ python3 safety-razer.py &
```

To run `safety-razer` automatically when you open a terminal, run:

```bash
$ echo "python3 safety-razer.py &" >> ~/.zshrc
```

