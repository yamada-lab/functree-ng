FROM python:3.6.2

LABEL maintainer="Yuta Yamate <yyamate@bio.titech.ac.jp>"

RUN curl https://nodejs.org/dist/v6.11.2/node-v6.11.2-linux-x64.tar.xz | tar Jxv -C /opt/
ENV PATH /opt/node-v6.11.2-linux-x64/bin:$PATH

RUN echo 'deb http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list \
	&& wget https://dl-ssl.google.com/linux/linux_signing_key.pub \
	&& apt-key add linux_signing_key.pub

RUN	apt-get update && apt-get install -y --no-install-recommends \
		unzip \
		google-chrome-stable \ 
	&& rm -rf /var/lib/apt/lists/*

RUN wget https://chromedriver.storage.googleapis.com/2.39/chromedriver_linux64.zip \ 
	&& unzip chromedriver_linux64.zip \
	&& mv chromedriver /usr/local/bin/ \
	&& rm chromedriver_linux64.zip

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
