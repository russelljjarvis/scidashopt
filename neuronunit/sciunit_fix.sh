#sudo /opt/conda/bin/pip install --upgrade pip
sudo /opt/conda/bin/pip uninstall -y sciunit
sudo rm -r /opt/conda/lib/python3.5/site-packages/quantities-0.11.1-py3.5.egg

pip install git+https://github.com/python-quantities/python-quantities

#sudo /opt/conda/bin/pip install execnet pandas
sudo /opt/conda/bin/pip install git+https://github.com/scidash/sciunit@dev
#sudo /opt/conda/bin/pip install olefile
git clone https://github.com/vrhaynes/AllenInstituteNeuroML.git
sudo /opt/conda/bin/pip install git+https://github.com/OpenSourceBrain/OpenCortex
sudo /opt/conda/bin/pip install -e neuronunit
sudo /opt/conda/bin/pip install -e BluePyOpt

sudo /opt/conda/bin/pip install git+https://github.com/NeuroML/pyNeuroML
rm -r /opt/conda/lib/python3.5/site-packages/PyLEMS-0.4.9-py3.5.egg
sudo /opt/conda/bin/pip install git+https://github.com/NeuroML/pyNeuroML


#wget --no-check-certificate --content-disposition https://github.com/OpenSourceBrain/AllenInstituteNeuroML/blob/master/CellTypesDatabase/models/GLIF/parse_glif.py
#sudo /opt/conda/bin/pip3 install git+https://github.com/OpenSourceBrain/AllenInstituteNeuroML.git

# wget --no-check-certificate --content-disposition https://raw.githubusercontent.com/OpenSourceBrain/AllenInstituteNeuroML/master/CellTypesDatabase/models/GLIF/run_glif.py
