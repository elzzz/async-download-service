# Downloading file service

Service helps the work of the main site, made on the CMS, and serves requests for downloading archives with files. 
Service can only pack files into the archive. Upload files to the server via FTP or CMS admin panel.

Creating an archive occurs on the fly upon request from the user. 
The archive is not stored on the disk, instead, as it is packaged, it is immediately sent to the user for download.

From unauthorized access, the archive is protected by a hash in the download link address, for example: `http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`. 
The hash is given by the name of the file directory, the directory structure looks like this:

```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```


## Prerequisites

- Docker 18.0+


## Installation

Use git to download the download service.

```bash
$ git clone https://github.com/elzzz/async-download-service.git
```

## Usage

```bash
$ cd async-download-service
$ docker-compose up -d
```

Service starts on port 8080. To check how it's working. [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

Afterwards, you can try to download files from `/archive/`. Example:

```
GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea/
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)   
