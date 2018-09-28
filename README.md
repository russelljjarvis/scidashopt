## Instructions for building with Docker on CENTOS server:
``` bash
mkdir git_opt
cd git_opt
Create a file called build.sh whose contents are:
#!/bin/bash
git clone -b scidash https://github.com/russelljjarvis/BluePyOpt
git clone -b dev https://github.com/russelljjarvis/neuronunit
wget https://raw.githubusercontent.com/russelljjarvis/scidashopt/master/Dockerfile
docker build -t scidash/neuronunit-optimization_juypter .
```
## END of file contents

Run build.sh with: 
`$bash build.sh`
Then enter the container (interactively):
```bash
docker run -it -v ~/git_opt/neuronunit:/home/jovyan/neuronunit -v ~/git_opt/BluePyOpt:/home/jovyan/BluePyOpt scidash/neuronunit-optimization_juypter /bin/bash
```
Inside the container confirm modules Neuronunit and BluePyOpt are importable.
```
$python 
>>>import neuronunit
>>>import bluepyopt
```
As a fake user, based on rjarvis@spike (must have same privileges, and group membership), can you create a repository, and git add/git commit ?
For example, can you make a pull from an existing git repository?
git pull https://github.com/russelljjarvis/d_test.git

reinitialise it:

git init
git add README.md
git commit -m "first commit"

# add a new remote:

git remote add origin https://github.com/user_name/d_test.git
git push -u origin master
