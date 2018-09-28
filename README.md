## Instructions for building with Docker on the CENTOS spike server:

* 1 create a new directory and navigate into it:
``` bash
mkdir git_opt
cd git_opt
```
* 2 Then, create a file called `build.sh` whose contents are:
```
#!/bin/bash
git clone -b scidash https://github.com/russelljjarvis/BluePyOpt
git clone -b dev https://github.com/russelljjarvis/neuronunit
wget https://raw.githubusercontent.com/russelljjarvis/scidashopt/master/Dockerfile
docker build -t scidash/neuronunit-optimization_juypter .
```

* 3 Run build.sh with: 
`$bash build.sh`

* 4 After the above commands/script is run then enter the container (interactively):
```bash
docker run -it -v ~/git_opt/neuronunit:/home/jovyan/neuronunit -v ~/git_opt/BluePyOpt:/home/jovyan/BluePyOpt scidash/neuronunit-optimization_juypter /bin/bash
```
* 5 Inside the container confirm modules Neuronunit and BluePyOpt are importable.
`$python` 

```
>>>import neuronunit
>>>import bluepyopt
```


* 6 Also while inside the container:
As a fake user, based on rjarvis@spike (must have same privileges, and group membership), can you create a repository, and git add/git commit ?

For example, can you make a pull from an existing git repository?
* 7 git clone https://github.com/russelljjarvis/d_test.git

* 8 reinitialise it:
```
git init
git add README.md
git commit -m "first commit"
```
On Github create a new repository, then use the repository URL as a new remote.

* 9. add a new remote:
```
git remote add origin https://github.com/user_name/reponame.git
git push -u origin master
```
