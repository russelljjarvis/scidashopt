import nbformat
import os
from nbconvert.preprocessors import ExecutePreprocessor
with open('progress_report.ipynb') as f:
    nb = nbformat.read(f, as_version=4)
ep = ExecutePreprocessor()
#ep = ExecutePreprocessor(timeout=5600, kernel_name='python3')
ep.preprocess(nb, {'metadata': {'path': os.getcwd()}})
with open('progress_report.ipynb', 'wt') as f:
    nbformat(nb, f)
