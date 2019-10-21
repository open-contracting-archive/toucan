# Contributing

## Developer notes

All reading and writing to disk should be done through the `DataFile` class in `default/data_file.py`. This makes it easier for developers to control and review how user-submitted data is managed, in particular with respect to security issues and disk usage.

## Maintainer notes

* To find instances of writing to disk outside the `DataFile` class, grep for `'w`
* To find instances of reading from disk outside the `DataFile` class, grep for `open\(`
