# FuncTree 2
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

FuncTree is a web application that allows users to map omics data onto a pre-defined radial tree (e.g. based on the [KEGG brite functional hierarchy](http://www.genome.jp/kegg-bin/get_htext?br08902.keg)) to help them quickly and comprehensively understand the functional potential of their data, and to develop further hypothesis and scientific insights.

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
##### Requirements
- Python 3
- Node.js
- MongoDB

Install dependencies and build the application:
```bash
$ pip3 install -r requirements.txt
$ npm install yarn --global
$ yarn run install-depends
$ yarn run install-devDepends
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

#### Loading of functional annotations from external sources (optional)
1. Download [generate-external-mapping.sh](/scripts/generate-external-mapping.sh) and edit `LIST_HOME` to match the location of your local KEGG distribution.
2. Run the script to generate the `external_annotation.map` file.
3. Add `external_annotation.map` to `/app/functree/static/data/ortholog_mapping/` (See the docker-compose.yml services:app:volumes for details)
4. Log into the admin console (e.g. http://localhost:8080/admin), then click the 'Update annotation mapping' link.

## Publications
- Uchiyama T, Irie M, Mori H, Kurokawa K, Yamada T. FuncTree: Functional Analysis and Visualization for Large-Scale Omics Data. PLoS One. 2015 May 14;10(5):e0126967. doi: 10.1371/journal.pone.0126967. eCollection 2015. PubMed PMID: 25974630; PubMed Central PMCID: PMC4431737.

## License
FuncTree 2 is released under the [MIT License](LICENSE).
