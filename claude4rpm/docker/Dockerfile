FROM openeuler/openeuler:24.03-lts

# Install build dependencies
RUN yum install -y \
    rpm-build \
    rpmdevtools \
    rpmlint \
    golang \
    git \
    wget \
    tar \
    spectool \
    sudo \
    && yum clean all

# Create builder user
RUN useradd -m builder && \
    echo "builder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to builder user
USER builder
WORKDIR /home/builder

# Setup rpmbuild directory structure
RUN rpmdev-setuptree

# Configure Go environment
ENV GOPROXY=https://goproxy.cn,direct
ENV GO111MODULE=on
ENV GOPATH=/home/builder/go

# Create mount points
RUN mkdir -p /home/builder/rpmbuild/SPECS \
    /home/builder/rpmbuild/SOURCES \
    /home/builder/rpmbuild/RPMS \
    /home/builder/rpmbuild/SRPMS

VOLUME ["/home/builder/rpmbuild"]

CMD ["/bin/bash"]
