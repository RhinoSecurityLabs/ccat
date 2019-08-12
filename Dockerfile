FROM docker:19.03.1

RUN apk update && apk add build-base python3 python3-dev && rm -rf /var/cache/apk/*

WORKDIR /app

COPY ./requirements.txt /app

RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]

CMD ["ccat.py"]