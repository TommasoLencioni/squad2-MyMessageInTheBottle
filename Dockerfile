FROM python:3.9.0a3-alpine3.10
WORKDIR /src
COPY . .
RUN apk add build-base
RUN apk add --update bash && rm -rf /var/cache/apk/*
RUN pip install -r requirements.txt
ENV FLASK_APP=monolith
ENV FLASK_ENV=development
ENV FLASK_DEBUG=true
CMD ["flask", "run","--host","0.0.0.0"]