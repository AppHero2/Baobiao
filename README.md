# amazon-book-query
Provide Amazon Book Query search result as a tsv file format

## Requirements
* Python 3.4, 3.5, 3.6

## Installation

Amazon Book Query may be installed with:
```
$ python setup.py install
```

Once installed, run following command at the commandline with:
```
$ amazon-book-query -h
```

That gives you usage instruction:
```
usage: amazon-book-query
```
## Enviroment varaiables:
```
AMAZON_ACCESS_KEY=amazon_access_key
AMAZON_SECRET_KEY=amazon_secret_key
AMAZON_ASSOC_KEY=amazon_associate_tag
```
## Required parameters:
    parameters for Amazon Book Query request

    -s SOURCE
                    source tsv file path
    -d DESTINATION
                    destination directory path to save output file as tsv format

## Example Usage
The following command provide a path of output tsv file after run Amazon Book Query request
```
$ amazon-book-query  -s "test.tsv"  -d "/~"

```
