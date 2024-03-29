FROM continuumio/miniconda3

RUN apt-get update && apt-get install -y build-essential
RUN conda install -c anaconda python=3.6 pip gxx_linux-64
RUN pip install pysurvival dash_table dash_bootstrap_components
RUN mkdir /jobczyk2020-app
COPY . /jobczyk2020-app
# RUN git clone https://github.com/kstawiski/jobczyk2020-app
RUN cd jobczyk2020-app && pwd
WORKDIR /jobczyk2020-app

EXPOSE 80
CMD ["python3","app.py"]
