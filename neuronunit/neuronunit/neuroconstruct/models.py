"""
Implementation of a model built in neuroConstruct.
http://www.neuroconstruct.org/
"""

import os
from datetime import datetime

from xml.etree.ElementTree import XML
import numpy as np

from pythonnC.utils import putils # From the neuroConstruct pythonnC package.  
from sciunit import Model
from neuronunit import CPYTHON,JYTHON
import neuronunit.capabilities as cap
from pythonnC.utils import neurotools as nc_neurotools
from .__init__ import NC_HOME
if CPYTHON:
    from pythonnC.utils import putils as utils # From the neuroConstruct pythonnC package.
    import numpy as np
if JYTHON:
    from pythonnC.utils import jutils as utils # From the neuroConstruct pythonnC package.
JUTILS_PATH = 'pythonnC.utils.jutils'


class NeuroConstructModel(Model,
                          cap.ProducesActionPotentials,
                          cap.ReceivesCurrent):
    """Implementation of a candidate model usable by neuroConstruct (written in neuroML).
    Execution takes places in the neuroConstruct program.
    Methods will be implemented using the neuroConstruct python
    API (in progress)."""

    def __init__(self, project_path, name=None, **kwargs):
        """file_path is the full path to an .ncx file."""
        #print("Instantiating a neuroConstruct model from %s." % project_path)
        self.project_path = project_path
        self.ran = False
        self.rerun = False
        self.always_rerun = False
        self.runtime_methods = {}
        self.sim_path = None
        self.current = self.Current()
        self.population_name = self.get_cell_group()+'_0'
        for key,value in kwargs.items():
            setattr(self,key,value)
        super().__init__(name=name, **kwargs)

    def get_ncx_file(self):
        # Get a list of .ncx (neuroConstruct) files.  Should be only one for most projects.
        ncx_files = [f for f in os.listdir(self.project_path) if f[-4:]=='.ncx']
        if not ncx_files:
            raise IOError("No .ncx files found in %s" % self.project_path)
        ncx_file = os.path.join(self.project_path,ncx_files[0]) # Get full path to .ncx file.
        return ncx_file

    def get_cell_group(self):
        ncx_file = self.get_ncx_file()
        with open(ncx_file,'r') as f:
            xml_str = f.read()
        neuroml = XML(xml_str) # The NeuroML file in parsable form.
        cell_group = neuroml.find("object/void[@property='allSimConfigs']/void/object/void[@property='cellGroups']/void/string").text
        return cell_group

    def prepare(self):
        if not hasattr(self,'gateway'):
            if CPYTHON:
                self.gateway = utils.open_gateway(useSocket=True,
                                        automatic_socket=utils.AUTOMATIC_SOCKET)
                cmd = 'import %s as j;' % JUTILS_PATH
                cmd += 'import sys;'
                cmd += 'j.sim = j.Sim(project_path="%s");' % self.project_path
                cmd += 'channel.send(0)'
                channel = self.gateway.remote_exec(cmd)
                channel.receive()
                #self.gateway.terminate()

    def run(self, only_generate=False):
        """Runs the model using jython via execnet and returns a
        directory of simulation results"""
        self.prepare()
        if self.ran is False or self.rerun is True or self.always_rerun is True:
            if only_generate:
                print("Generating simulation files...")
            else:
                print("Running simulation...")
            self.sim_path = utils.run_sim(project_path=self.project_path,
                                          only_generate=only_generate,
                                          useSocket=True,
                                          useNC=True,
                                          useNeuroTools=True,
                                          runtime_methods=self.runtime_methods,
                                          gw=self.gateway)
            self.run_t = datetime.now()
            self.ran = not only_generate
            self.rerun = False
            del self.gateway
        else:
            print("Already ran simulation...")

    def get_membrane_potential(self, **kwargs):
        """Returns a neo.core.AnalogSignal object"""

        if self.sim_path is None or self.ran is False \
            or self.rerun or self.always_rerun:
            self.run(**kwargs)
        if self.sim_path == '':
            vm = None
        else:
            #print("Getting membrane potential...")#" from %s/%s" \
            #     % (self.sim_path,self.population_name))
            vm = nc_neurotools.get_analog_signal(self.sim_path,
                                                 self.population_name)
            # An AnalogSignal instance.
        return vm

    def get_spike_train(self, **kwargs):
        """Returns a neo.core.SpikeTrain object"""
        vm = self.get_membrane_potential(**kwargs)
        # A neo.core.AnalogSignal object
        return cap.spike_functions.get_spike_train(vm)

    def get_APs(self, **kwargs):
        """Returns a neo.core.SpikeTrain object"""
        vm = self.get_membrane_potential(**kwargs)
        # A neo.core.AnalogSignal object
        return cap.spike_functions.get_spike_train(vm)

    class Current(object):
        ampl = 0
        duration = 0
        offset = 0

    def inject_square_current(self, injected_current):
        self.prepare()
        cmd = 'import %s as j;' % JUTILS_PATH
        cmd += 'import sys;'
        cmd += 'err = j.sim.set_current_ampl(%f);' % \
                    injected_current['amplitude']
        cmd += 'channel.send(err);'
        channel = self.gateway.remote_exec(cmd)
        #print(cmd)
        err = channel.receive() # This will be an error code.
        if err:
            raise NotImplementedError(err)
        #self.current.ampl = current_ampl
        #self.runtime_methods['set_current_ampl']=[current_ampl]


class FakeNeuroConstructModel(NeuroConstructModel):
    """A fake neuroConstruct model that generates a gaussian noise
    membrane potential with some 'spikes'. Eventually I will make the membrane
    potential and the spikes change as a function of the current."""

    def __init__(self, *args, **kwargs):
        super(FakeNeuroConstructModel,self).__init__(*args,**kwargs)
        self.current_ampl = 0

    def run(self, **kwargs):
        n_samples = getattr(self,'n_samples',10000)
        self.vm = np.random.randn(n_samples)-65.0 # -65 mV with gaussian noise.
        for i in range(200,n_samples,200): # Make 50 spikes.
            self.vm[i:i+10] += 10.0*np.array(range(10)) # Shaped like right triangles.
        super(FakeNeuroConstructModel,self).run(**kwargs)

    def set_current_ampl(self,current):
        self.current_ampl = current


class OSBModel(NeuroConstructModel):
    """A model hosted on Open Source Brain (http://www.opensourcebrain.org).
    Will be in NeuroML format, and run using neuroConstruct."""

    def __init__(self,brain_area,cell_type,model_name,**kwargs):
        project_path = os.path.join(self.models_path,
                                    brain_area,
                                    cell_type,
                                    model_name,
                                    "neuroConstruct")
        if 'name' not in kwargs.keys():
            self._name = u'%s/%s/%s' % (brain_area,cell_type,model_name)
        NeuroConstructModel.__init__(self,project_path,**kwargs)
        self.name = model_name

    @classmethod
    def make_model(self,brain_area,cell_type,model_name,**kwargs):
        project_path = os.path.join(self.models_path,
                                    brain_area,
                                    cell_type,
                                    model_name,
                                    "neuroConstruct")
        return NeuroConstructModel(project_path,**kwargs)

    models_path = putils.OSB_MODELS


# DEPRECATED. 
class DEPRECATED_NeuroML2Model(NeuroConstructModel):
    """A model hosted on Open Source Brain (http://www.opensourcebrain.org).
    Will be in NeuroML format, and run using neuroConstruct."""

    def __init__(self,model_name,**kwargs):
        project_path = os.path.join(self.models_path,
                                    model_name)
        if 'name' not in kwargs.keys():
            self._name = u'%s' % (model_name)
        #self.create_nc_project()
        NeuroConstructModel.__init__(self,project_path,**kwargs)

    models_path = putils.NEUROML2_MODELS
 
    def create_nc_project(self):
        """Creates a neuroConstruct project from the NeuroML2 file(s)."""
        from java.io import File
        from ucl.physiol.neuroconstruct.project import Project
        from ucl.physiol.neuroconstruct.cell.converters import MorphMLConverter
        project = Project.createNewProject('/Users/rgerkin/', self.model_name, None)
        morphDir = File("%s/osb/showcase/neuroConstructShowcase/Ex3_Morphology/importedMorphologies/" % NC_HOME)
        morphmlFile = File(morphDir, "SimplePurkinjeCell.morph.xml")
        converter = MorphMLConverter()
        cell = converter.loadFromMorphologyFile(morphmlFile, "NewCell")
        project.cellManager.addCellType(cell) # Actually add it to the project
        project.cellGroupsInfo.setCellType("DefaultCellGroup", cell.getInstanceName()) # Set the type of an existing cell group to this
        project.saveProject()
