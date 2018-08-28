import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os

with open('progress_report.ipynb') as f:
    nb = nbformat.read(f, as_version=4)

ep = ExecutePreprocessor(timeout=4600, kernel_name='python3')
succeeded = ep.preprocess(nb, {'metadata': {'path': str(os.getcwd())}})
    
with open('progress_report.ipynb', 'wt') as f:
    nbformat.write(nb, f)
