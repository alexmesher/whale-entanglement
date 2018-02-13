FROM continuumio/miniconda3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN conda config --add channels conda-forge
RUN conda install -c conda-forge geopandas
RUN conda install -c conda-forge fiona
ADD . /code/