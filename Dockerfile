FROM python:3.6.2

LABEL maintainer="Yuta Yamate <yyamate@bio.titech.ac.jp>"

RUN curl https://nodejs.org/dist/v6.11.2/node-v6.11.2-linux-x64.tar.xz | tar Jxv -C /opt/
ENV PATH /opt/node-v6.11.2-linux-x64/bin:$PATH

ADD . /app/
WORKDIR /app/

RUN pip3 install -r requirements.txt
RUN npm install --global yarn && \
  yarn install && \
  yarn run bower install && \
  yarn run build

RUN pip3 install -r docs/requirements.txt
RUN cd docs && make html

EXPOSE 3031 8080

CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]
