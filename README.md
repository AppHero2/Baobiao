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
$ amazon-book-query --help
```

That gives you usage instruction:
```
usage: amazon-book-query
```

required parameters:
    parameters for Amazon Book Query request

    --source_path SOURCE_PATH
                    source tsv file path
    --destination_path DESTINATION_PATH
                    destination file path to save output file as tsv format

## Example Usage
The following command provide a path of output tsv file after run Amazon Book Query request
```
$ amazon-book-query  test.tsv  test1.tsv
```