# FuncTree 2
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

FuncTree is a web application that allows user to map omics data onto a pre-defined radial tree (e.g. based on the [KEGG brite functional hierarchy](http://www.genome.jp/kegg-bin/get_htext?br08902.keg)) to help them to quickly and comprehensively understand the functional potential of their data, and to develop further hypothesis and scientific insights.

## Requirements
- Python 3
- Node.js
- MongoDB

## Installation
Clone this repository and change directory to `functree-ng`:
```bash
$ git clone --recursive https://github.com/yamada-lab/functree-ng.git
$ cd functree-ng
```
## Building and running the application
#### Using Docker and Docker Compose (preferred and supported way)
Execute the command below. `docker-compose` will automatically set up Docker containers:
```bash
$ docker-compose up
```
Then open http://localhost:8080 in your web browser.

##### Automatic transpilation, for dev mode only (optional)
To enable automatic transpilation of ECMAScript and SCSS in dev mode, enter the docker instance 
```
docker exec -it functree-ng_app_1 /bin/bash
```

then issue the following commands
```
yarn babel:watch
yarn sass:watch
```

#### Manual installation (unsupported, use at your own risk)
Install dependencies and build the application:
```bash
$ pip3 install -r requirements.txt
$ npm install yarn --global
$ yarn install
$ yarn run bower install
$ yarn run build
```
Start up the application:
```bash
$ uwsgi --ini uwsgi.ini
```
Then open http://localhost:8080 in your web browser.


## Configuration
To configure the behavior of the application, create `instance/config.py` with the same format as `functree/config.py`.

## Publications
- Uchiyama T, Irie M, Mori H, Kurokawa K, Yamada T. FuncTree: Functional Analysis and Visualization for Large-Scale Omics Data. PLoS One. 2015 May 14;10(5):e0126967. doi: 10.1371/journal.pone.0126967. eCollection 2015. PubMed PMID: 25974630; PubMed Central PMCID: PMC4431737.

## License
FuncTree 2 is released under the [MIT License](LICENSE).
