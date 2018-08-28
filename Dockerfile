# author Russell Jarvis rjjarvis@asu.edu
# author Rick Gerkin rgerkin@asu.edu
# neuronunit-showcase

FROM scidash/neuronunit
USER root
RUN apt update -y
RUN apt upgrade -y
RUN apt-get upgrade python
RUN apt-get update
RUN apt-get install -y gvfs-bin libxss1 python3-setuptools
RUN apt-get install -y python-tk curl apt-utils
RUN sudo chown -R jovyan /home/jovyan/.cache



RUN pip install --upgrade pip
RUN pip install matplotlib
RUN pip install IPython \
                notebook \
                ipykernel \
                enum34 \
		numba
RUN conda info --envs
RUN conda update -n root conda
RUN pip install pillow zmq --upgrade
RUN pip install pyzmq 

RUN easy_install gevent
RUN easy_install greenlet
RUN easy_install cloudpickle

RUN pip install zmq
RUN pip install --upgrade zmq pip

RUN pip uninstall -y tornado
RUN pip install tornado==4.5.3



RUN pip install alembic dask distributed

ENV PATH $PATH:/opt/conda/bin
ENV PATH $PATH:/opt/conda/bin/ipython
ENV PATH $PATH:/opt/conda/bin/pip
ENV PATH $PATH:/opt/conda/bin/python
ENV PATH $PATH:/opt/conda/lib/python3.5/site-packages
ENV PATH $PATH:$PYTHONPATH

# RUN conda update -n base conda
USER $NB_USER

ADD neuronunit neuronunit
WORKDIR neuronunit
RUN pip install -e .

WORKDIR $HOME

ADD BluePyOpt BluePyOpt
WORKDIR BluePyOpt
RUN pip install -e .
WORKDIR $HOME

RUN printenv PATH
RUN python -c "import pyneuroml"
RUN python -c "import neuronunit"
RUN python -c "import quantities"
RUN python -c "import neuron"
RUN python -c "import pyneuroml"
RUN nrnivmodl
RUN nrniv
WORKDIR $HOME
#RUN sudo chown -R $NB_USER $HOME
ENV PYTHONPATH $HOME/neuronunit:$PYTHONPATH
RUN pip install -U jupyter
RUN pip install chardet idna

RUN echo "install BBO"
WORKDIR $HOME

WORKDIR $HOME
RUN python3 -c "import bluepyopt"
RUN pip install radon -U
RUN pip install jupyter -U
