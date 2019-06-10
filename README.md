# Shout

_When declaring your logs is not enough_

## Usage

```bash
shout -u TIC-DVC4 -p bomberman -s "2019-06-3 9:00" -e "2019-06-3 12:00" -d declaration.md
```

## Requirements

`shout` expects to have your credentials available as environment variables.
This _could_ change in the future, but it's just the way it is right now.

Please provide the following before attempting to use this utility:

- `ETNA_USER` - Your `login`
- `ETNA_PASS` - The password you use to log in the intranet

## Installation

```bash
pip install --upgrade shout
```

## Example declaration

_Might get autogenerated or something in the future_

```markdown
Objectifs: Achieve something
Actions: Do something
Resultats: Something does foo
```


## Notice

In case you'd consider this shady in any way, the entirety of the source code is available for you to read.

Etnawrapper: https://github.com/tbobm/etnawrapper
