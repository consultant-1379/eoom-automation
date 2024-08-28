FROM armdocker.rnd.ericsson.se/proj-ldc/common_base_os/sles:3.45.0-15 as release

# initialize a "user" for python logging output.
ARG USERNAME='cicd-user'

RUN zypper ar -C -G -f https://arm.sero.gic.ericsson.se/artifactory/proj-ldc-repo-rpm-local/common_base_os/sles/3.45.0-15 LDC-CBO-SLES \
 && zypper ref -f -r LDC-CBO-SLES \
 && zypper install -y python39 python39-pip curl unzip apache2-utils\
 && zypper clean --all \
 && find /usr -type d -name  "__pycache__" -exec rm -r {} +

# A locale needs to be installed and set for later use by some python packages like click
ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8
ENV PYTHONIOENCODING='utf-8'
ENV PYTHONDONTWRITEBYTECODE='x'

# Download helm 3 binary for later inclusion in final image.
WORKDIR /helm3/
RUN curl -O https://arm1s11-eiffel052.eiffel.gic.ericsson.se:8443/nexus/service/local/repositories/eo-3pp-foss/content/org/cncf/helm/3.7.1/helm-3.7.1.zip  \
 && unzip helm-3.7.1.zip && rm helm-3.7.1.zip \
 && mv /helm3/linux-amd64/helm /usr/bin/helm \
 && helm version

# Download helmfile binary for later inclusion in final image.
WORKDIR /helmfile/
RUN curl -O https://arm1s11-eiffel052.eiffel.gic.ericsson.se:8443/nexus/service/local/repositories/eo-3pp-tools/content/com/helm/helmfile/0.139.9/helmfile-0.139.9.zip \
 && unzip helmfile-0.139.9.zip && rm helmfile-0.139.9.zip \
 && mv /helmfile/helmfile_linux_amd64 /usr/bin/helmfile \
 && helmfile version

# Download kubectl binary for later inclusion in final image.
WORKDIR /usr/bin
RUN curl -sL https://arm1s11-eiffel052.eiffel.gic.ericsson.se:8443/nexus/content/repositories/eo-3pp-foss/org/cncf/kubernetes/kubectl/1.22.0/kubectl-1.22.0.zip -o kubectl.zip \
 && unzip kubectl.zip && rm kubectl.zip \
 && kubectl --help

ENV USER=${USERNAME}

ENV VIRTUAL_ENV=/opt/esoa_staging

RUN python3.9 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m pip install --no-cache-dir --upgrade pip==23.2.1

COPY requirements-docker.txt .

RUN pip install --no-cache-dir --upgrade --extra-index-url https://arm.sero.gic.ericsson.se/artifactory/api/pypi/proj-vnfci-pypi-local/simple/ -r requirements-docker.txt

USER ${USERNAME}

WORKDIR /esoa-automation/

ENTRYPOINT ["python"]
