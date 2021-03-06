# mdbread-alpine
[![Docker Pulls](https://img.shields.io/docker/pulls/mio101/mdbread-alpine.svg)](https://hub.docker.com/r/mio101/mdbread-alpine)
[![Docker Stars](https://img.shields.io/docker/stars/mio101/mdbread-alpine.svg)](https://hub.docker.com/r/mio101/mdbread-alpine)
[![Docker Automated buil](https://img.shields.io/docker/automated/mio101/mdbread-alpine.svg)](https://hub.docker.com/r/mio101/mdbread-alpine)


Read data from MS Access MDB files by Python, **only read**, built on [alpine](https://alpinelinux.org).

### Based on:

* [MDB Tools](https://github.com/brianb/mdbtools) MDB Tools is a set of programs to help you use Microsoft Access file in various settings.
* [mdbread](https://github.com/gilesc/mdbread) A simple Cython-based wrapper for the excellent MDBTools package to read data from MS Access MDB files.

Thanks these two amazing projects.

### What this project did
* Compile and install MDB Tools on alpine.
* Remove mdbread's DEPRECATED code, remove pandas for a smaller size image and easy to build, then install mdbread.


## Note
1. You can modify the file `repositories` to change the repositories of apk(Alpine Linux package management) for a faster download. 
2. Mdbread use pandas (a famous python data analyis packages) to return `DataFrame` object, i remove the pandas to save about half size of this image(235MB > 123MB). If u need `DataFrame` object, u can modify mdbread/mdbread.pyx and Dockerfile to add pandas support, there's a [tag](https://github.com/MioYvo/mdbread-alpine/tree/with-pandas) in github that built with pandas, it would help.

## How to use
* Pull and test

    ```
    >> docker run mio101/mdbread-alpine python -c "import mdbread;print(mdbread)"
    
    Unable to find image 'mio101/mdbread-alpine:latest' locally
    latest: Pulling from mio101/mdbread-alpine
    2aecc7e1714b: Already exists
    665060bf69b5: Pull complete
    7d37ce5e6761: Pull complete
    24e603a66a49: Pull complete
    Digest: sha256:378300b9e6a7803907cda9fe7e98b2859e78ba1426cb76fd40eabd87d66bc36b
    Status: Downloaded newer image for mio101/mdbread-alpine:latest
    <module 'mdbread' from '/usr/lib/python2.7/site-packages/mdbread.so'>
    ```
    Notice the last line that printed info of module mdbread, it means that the mdbread module has been successfully loaded.

* mdbread Usage

    * From [mdbread](https://github.com/gilesc/mdbread#usage)
    
        ```
        >>> import mdbread
        >>> db = mdbread.MDB("MyDB.mdb")
        >>> print db.tables
        ["tbl1", "tbl2", "tbl3"]
        
        >>> tbl = db["tbl1"]
        >>> print tbl.columns
        ["foo","bar","baz"]
        ```
        To get the data in a table, you have three options:
        
        `mdbread.Table.records()` returns a generator of dictionaries, where the keys are column names and the values are the data.
        
        `iter(mdbread.Table)` will return a namedtuple for each row. You can also use this form with `for row in tbl:`
        
        >NOT SUPPORT IN THIS PROJECT: `mdbread.Table.to_data_frame()` will return a pandas `DataFrame ` containing all the data for the entire table (possibly requiring lots of memory).
    
    * Tips
    
        `mdbread.Table.records()` and `iter(mdbread.Table)` will return a generator of [namedtuple](https://docs.python.org/2/library/collections.html#collections.namedtuple), it's convenience to use for dealing with data, bravo :)
