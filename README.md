# knora-tests
Different tests which can be run against a running Knora stack

## 01_import_test

A python based test importing 2000 resources with 8 images

## 01_import_test_graphdb

A replayable (http://goreplay.org) GraphDB requests file based on the `01_import_test`

Usage:

```
# unpack
$ tar -xzvf graphdb_requests.gor.tar.gz

# Run with normal speed. For load testing, run with speeds higher 100%.
$ goreplay --input-file "requests_0.gor|100%" --output-http "localhost:7200"
```

