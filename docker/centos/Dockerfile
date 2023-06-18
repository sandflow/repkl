FROM centos:7.9.2009
SHELL [ "/bin/bash", "-c" ]
ENV SHELL=/bin/bash
## NOTE TO USER: it's imparative that you call this docker file from a shell session that has its current directory as the root of the directory for the repkl repo. Otherwise errors will result when using this dockerfile.

## allow user to send values to these via --build-args http_proxy=http://my.proxyserver.net:<port> in the 'docker build'  process. If not passed, these are ignored.
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV http_proxy=${http_proxy}
ENV https_proxy=${https_proxy}


RUN yum -y update && yum -y install epel-release
## install developer tools 
RUN yum -y groupinstall "Development Tools"
RUN yum -y install openssl-devel bzip2-devel libffi-devel xz-devel wget curl

# must compile python >= python3.8
RUN wget https://www.python.org/ftp/python/3.8.16/Python-3.8.16.tgz
RUN tar xvf Python-3.8.16.tgz
RUN cd Python-3.8*/ && \
./configure --enable-optimizations && \
make altinstall 


RUN yum -y install epel-release
RUN yum -y install which
RUN mkdir /usr/src/repkl
WORKDIR /usr/src/repkl
# Copy from the current dir on the host machine. I.E. `docker build` command needs to be called while within the main directory of https://github.com/sandflow/repkl. Files will be copied into this docker container, in the dir: /usr/src/repkl as specified in WORKDIR, above.
COPY . .

# set environment variables, and make python 3.8 the default python. Allow easy switch to other python
RUN echo LC_ALL=en_US.utf-8 > ~/.profile && \
echo LANG=en_US.utf-8 >> ~/.profile && \
source ~/.profile && \
alternatives --install /usr/bin/python python /usr/bin/python2 50 && \
alternatives --install /usr/bin/python python /usr/local/bin/python3.8 60 && \
alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.8 60 && \
python -m pip install --upgrade pip && \
pip install pipenv && \
cd /usr/src/repkl && \
echo PYTHONPATH=src/main/python >> /etc/environment
WORKDIR /usr/src/repkl
ENV PYTHONPATH=src/main/python
RUN echo source /etc/environment >> /root/.bashrc
RUN echo source /root/.profile >> /root/.bashrc
RUN source /root/.bashrc

# Install pipenv based repkl dev environment, and test run repkl.
RUN PYTHONPATH=src/main/python pipenv install --dev 
RUN PYTHONPATH=src/main/python pipenv run python src/main/python/repkl/cli.py -h

## the above allws one to start a bash shell in the container and do dev work with repkl

## the below is the build of repkl from pip repo for typical running

RUN pip install -i https://test.pypi.org/simple/ repkl
WORKDIR /usr/src/repkl

ENTRYPOINT ["repkl"]
