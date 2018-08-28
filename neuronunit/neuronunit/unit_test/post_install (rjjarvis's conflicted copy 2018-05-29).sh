cd $HOME
pip install dask distributed
sudo /opt/conda/bin/pip install -e BluePyOpt
sudo /opt/conda/bin/pip install -e neuronunit
sudo /opt/conda/bin/pip install git+htts//github.com/scidash/sciunit.git@dev

sudo rm -r /opt/conda/lib/python3.5/site-packages/PyLEMS-0.4.9-py3.5.egg
sudo /opt/conda/bin/pip install git+https://github.com/NeuroML/pyNeuroML

cd $HOME/neuronunit/neuronunit/unit_test
ipython -i pipe_entry_point.py
