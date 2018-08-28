from sciunit.utils import NotebookTools,import_all_modules
import os
path = os.getcwd()
name = path + str('/test_ga_versus_grid')
nt = NotebookTools()
nt.do_notebook(name)
