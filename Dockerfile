# author Russell Jarvis rjjarvis@asu.edu
# author Rick Gerkin rgerkin@asu.edu
# neuronunit-showcase

FROM scidash/neuronunit

#################
# Showcase for model optimization using NeuronUnit.
#################
USER root

RUN apt-get update
RUN apt-get install -y gvfs-bin libxss1 python3-setuptools
RUN apt-get install -y python-tk curl apt-utils

#RUN sudo chown -R jovyan $HOME
#RUN sudo chown -R jovyan /opt/conda/lib/python3.5/site-packages/

RUN pip install --upgrade pip
RUN pip install matplotlib
RUN pip install IPython \
                jupyterhub \
                notebook \
                ipykernel \
                enum34 \
		numba
RUN conda info --envs
RUN conda update -n root conda

# RUN conda update -n base conda
#numba is for optimized code, bqplot is for interactive plotting.
RUN conda install -c dask distributed
RUN pip install pyzmq
RUN conda install -c anaconda pyzmq
RUN conda install -c anaconda libsodium
# RUN pip install libsodium

RUN easy_install gevent
RUN easy_install greenlet
RUN pip install cloudpickle dask distributed

ENV PATH $PATH:/opt/conda/bin
ENV PATH $PATH:/opt/conda/bin/ipython
ENV PATH $PATH:/opt/conda/bin/pip
ENV PATH $PATH:/opt/conda/bin/python
ENV PATH $PATH:/opt/conda/lib/python3.5/site-packages
ENV PATH $PATH:$PYTHONPATH

RUN pip install dask
RUN pip install tornado zmq
RUN pip install --upgrade zmq tornado pip

# RUN conda update -n base conda
USER $NB_USER

RUN printenv PATH
RUN python -c "import pyneuroml"
RUN python -c "import neuronunit"
# RUN python -c "from neuronunit.models.reduced import ReducedModel"
RUN python -c "import quantities"
RUN python -c "import neuron"
RUN python -c "import pyneuroml"
RUN nrnivmodl
RUN nrniv
WORKDIR $HOME
RUN sudo chown -R $NB_USER $HOME
ENV PYTHONPATH $HOME/neuronunit:$PYTHONPATH
RUN pip install -U jupyter
RUN echo "install NU"

ADD neuronunit neuronunit
WORKDIR neuronunit
RUN sudo /opt/conda/bin/pip install -e .

RUN echo "install BBO"
WORKDIR $HOME
ADD BluePyOpt BluePyOpt
WORKDIR BluePyOpt
RUN sudo /opt/conda/bin/pip install -e .
WORKDIR $HOME
RUN ipython -c "import bluepyopt"

# ENTRYPOINT /bin/bash
# RUN pip uninstall tornado
