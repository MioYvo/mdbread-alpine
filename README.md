# mdbread-alpine

Read data from MS Access MDB files by Python, **only read**, built on [alpine](https://alpinelinux.org).

### Base on:

* [MDB Tools](https://github.com/brianb/mdbtools) MDB Tools is a set of programs to help you use Microsoft Access file in various settings.
* [mdbread](https://github.com/gilesc/mdbread) A simple Cython-based wrapper for the excellent MDBTools package to read data from MS Access MDB files.

Thanks these two amazing projects.

### What this project did
* Compile and install MDB Tools on alpine to get a smaller size image than other linux os like ubuntu
* remove mdbread's DEPRECATED code


## Note
1. You can modify file `repositories` to change the repositories of apk(Alpine Linux package management). ~~In this project, I use ustc's apline repository because I am in China, it's very slow to download packages from alpine's default repository.~~
