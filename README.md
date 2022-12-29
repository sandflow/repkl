# IMF Composition Repackager (repkl)

                                         88         88
                                         88         88
                                         88         88
    8b,dPPYba,   ,adPPYba,  8b,dPPYba,   88   ,d8   88
    88P'   "Y8  a8P_____88  88P'    "8a  88 ,a8"    88
    88          8PP"""""""  88       d8  8888[      88
    88          "8b,   ,aa  88b,   ,a8"  88`"Yba,   88
    88           `"Ybbd8"'  88`YbbdP"'   88   `Y8a  88
                            88
                            88

## Introduction

IMF Composition Repackager (repkl) creates a new Delivery (the destination) from
a single Composition (the target) whose assets are located across one or more
source Deliveries. The assets of the target can be either copied, moved or
symlinked from the source deliveries.

`repkl` is written in pure Python.

## Quick start

* run `pipenv install --dev`
* set the `PYTHONPATH` environment variable to `src/main/python`, e.g. `export PYTHONPATH=src/main/python`
* `pipenv run` can then be used:

```sh
pipenv install --dev
export PYTHONPATH=src/main/python
pipenv run python src/main/python/replk/cli.py <path to the target CPL> <path to the destination directory>
```

## Dependencies

### Runtime

* [python >= 3.8](https://python.org)

### Development

The project uses [pipenv](https://pypi.org/project/pipenv/) to manage dependencies.

* [pylint](https://pypi.org/project/pylint/)
* [coverage](https://pypi.org/project/coverage/)