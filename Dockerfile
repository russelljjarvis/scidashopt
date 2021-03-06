#################
# Showcase for model optimization using NeuronUnit.
#################

FROM scidash/neuronunit
USER root
RUN apt-get install -y locate apt-utils

RUN apt-get update
RUN apt-get install -y gvfs-bin libxss1 python3-setuptools
RUN apt-get install -y python-tk curl apt-utils
RUN sudo chown -R jovyan /home/jovyan/.cache

RUN pip install --upgrade pip
RUN pip install matplotlib
RUN pip install IPython \
                jupyterhub \
                notebook \
                ipykernel \
                enum34 \
        numba

RUN conda install dask distributed


RUN easy_install gevent
RUN easy_install greenlet

ENV PATH $PATH:/opt/conda/bin
ENV PATH $PATH:/opt/conda/bin/ipython
ENV PATH $PATH:/opt/conda/bin/pip
ENV PATH $PATH:/opt/conda/bin/python
ENV PATH $PATH:/opt/conda/lib/python3.5/site-packages
ENV PATH $PATH:$PYTHONPATH

RUN pip install dask distributed toolz
RUN pip install tornado zmq
RUN pip install --upgrade zmq tornado pip
RUN conda install -c anaconda pyzmq
RUN conda install -c conda-forge libsodium
RUN pip install dask distributed toolz
WORKDIR $HOME
RUN pip install --upgrade pandas

ADD neuronunit neuronunit
WORKDIR neuronunit


RUN pip install -e .

WORKDIR $HOME
ADD BluePyOpt BluePyOpt
WORKDIR BluePyOpt
RUN pip install -e .
WORKDIR $HOME


USER jovyan

RUN sudo chown -R jovyan $HOME


RUN printenv PATH
RUN python -c "import bluepyopt"

RUN python -c "import pyneuroml"
RUN python -c "import neuronunit"
# RUN python -c "from neuronunit.models.reduced import ReducedModel"
RUN python -c "import quantities"
RUN python -c "import neuron"
RUN python -c "import pyneuroml"
RUN nrnivmodl
RUN nrniv
WORKDIR $HOME

RUN git clone https://github.com/OpenSourceBrain/IzhikevichModel.git

WORKDIR $HOME/neuronunit/neuronunit/unit_test
ENTRYPOINT /bin/bash
