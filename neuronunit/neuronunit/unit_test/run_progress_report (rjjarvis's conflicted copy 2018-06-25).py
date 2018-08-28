import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os

with open('progress_report.ipynb') as f:
    nb = nbformat.read(f, as_version=4)
ep = ExecutePreprocessor(timeout=5600, kernel_name='python3')
ep.preprocess(nb, {'metadata': {'path': os.getcwd() }})
with open('progress_report.ipynb', 'wt') as f:
    nbformat.write(nb, f)
