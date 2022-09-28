FROM python:3.8
RUN mkdir -p /opt/project
WORKDIR /opt/project
COPY . .
RUN pip install -r api/requirements.txt
CMD python api/main.py