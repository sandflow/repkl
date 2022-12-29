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

## Command line

Run the following for command line options.

`python src/main/python/replk/cli.py -h`

Example (creates a supplementatl delivery where the assets are symlinked to the source assets):

`python src/main/python/replk/cli.py --action symlink --ov delivery/CPL_bb2ce11c-1bb6-4781-8e69-967183d02b9b delivery/CPL_0b976350-bea1-4e62-ba07-f32b28aaaf30.xml new_delivery/`

## Dependencies

### Runtime

* [python >= 3.8](https://python.org)

### Development

The project uses [pipenv](https://pypi.org/project/pipenv/) to manage dependencies.

* [pylint](https://pypi.org/project/pylint/)
* [coverage](https://pypi.org/project/coverage/)