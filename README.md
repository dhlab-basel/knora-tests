# knora-tests
Different tests which can be run against a running Knora stack

## Prerequisits

To be able to run `ab` (apache bench) with a high number of concurrent users, we need to possibly
raise some system limits.

On the Mac:

```
$ sysctl kern.maxfiles
kern.maxfiles: 98304
$ sysctl kern.maxfilesperproc
kern.maxfilesperproc: 49152
$ sudo sysctl -w kern.maxfiles=1048600
kern.maxfiles: 12288 -> 1048600
$ sudo sysctl -w kern.maxfilesperproc=1048576
kern.maxfilesperproc: 10240 -> 1048576
$ ulimit -S -n
7168
$ ulimit -S -n 1048576
$ ulimit -S -n
1048576
```


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

