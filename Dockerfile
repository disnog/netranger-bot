FROM python:3.7
WORKDIR /usr/src/app
COPY requirements.txt ./
COPY network_ranger ./network_ranger
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "network_ranger" ]