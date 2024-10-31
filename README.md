# KMS (Key & Mouse Sharing on lnetwork)

This little project is aimed to recreate a simple python version of Synergy/ShareMouse kind of application: sharing a mouse/keyboard over multiple connected computers.
For now, this is only compatible with Windows.


## Installation (On Linux)
Create a python environment (using for exampel miniconda) then:
```
  pip install -r requirements.txt
```

## How to run: 

```
  <host machine:>
    ifconfig | grep inet
    <get ip address>
    python main.py

  <client machine:>
    python3 client.py <ip of host>
```

## How to use

```

```
