FROM python:3.11-slim
RUN apt-get update && apt-get install -y x3270 && rm -rf /var/lib/apt/lists/*
RUN pip3 install tessia-baselib ansible
WORKDIR /workspace
