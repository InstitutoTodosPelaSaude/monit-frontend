FROM python:3.9-slim

WORKDIR /streamlit/app
COPY requirements.txt /streamlit/app/requirements.txt


RUN apt-get update \
    && apt-get -y install libpq-dev gcc --fix-missing
RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
