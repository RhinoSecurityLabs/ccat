# Rhino Container Hack CLI
_Rhino Container Hack CLI is a tool for testing security of container environments.

## Installation

To install Rhino Container Hack CLI from source

```
  $ git clone https://github.com/RhinoSecurityLabs/container-hack.git
  $ cd container-hack
  $ python3 setup.py install
  $ python3 main.py
```

Or run with Dcoker
```
  $ docker run -it --rm -v ~/.aws:/root/.aws/ -v /var/run/docker.sock:/var/run/docker.sock -v ${PWD}:/app/ rhinosecuritylabs/container-hack:latest
```

## Basic Usage

## Disclaimer

* Rhino Container Hack CLI is tool that comes with absolutely no warranties whatsoever. By using Rhino Container Hack CLI, you take full responsibility for any and all outcomes that result.
