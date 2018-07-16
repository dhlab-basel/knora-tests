# knora-tests
Different tests which can be run against a running Knora stack

## Prerequisits

To replay the HTTP request we use [Goreplay](https://goreplay.org). Please follow
their installation instructions.


## 01_import_test

A python based test importing 2000 resources with 8 images.

Usage:

```
$ cd 01_import_test
$ ./run.py
```

HTTP request capture with Goreplay (using the GraphDB port as an example):

```
# capture to file 
$ sudo goreplay --input-raw localhost:7200 --output-file requests.gor

# replay from file
$ goreplay --input-file requests_0.gor --output-http "localhost:7200"
```

## 01_import_test_graphdb

A replayable (http://goreplay.org) GraphDB requests file based on the `01_import_test`

Usage:

```
# re-initialize GraphDB with `graphdb-se-local-knora-test.sh` script.

# unpack
$ tar -xzvf graphdb_requests.gor.tar.gz

# Run with normal speed. For load testing, run with speeds higher 100%.
$ goreplay --input-file "requests_0.gor|100%" --output-http "localhost:7200"
```

