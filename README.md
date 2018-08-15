# knora-tests
Different tests which can be run against a running Knora stack

## Prerequisits

To replay the HTTP request we use [Goreplay](https://goreplay.org). Please follow
their installation instructions.


## import-test

A python based test importing 2000 resources with 8 images.

Usage:

```
$ cd import-test
$ ./run.py
```

## perftests

Gatling based tests with scenarios for basic, load and stress tests.

Usage:
```
$ sbt test
```

