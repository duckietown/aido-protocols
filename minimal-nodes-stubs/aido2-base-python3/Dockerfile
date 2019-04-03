FROM python:3.7
WORKDIR /project

RUN apt-get update && apt-get install -y ffmpeg mencoder && apt-get clean && \
    rm -r /var/lib/apt/lists/*


RUN pip install -U pip


COPY requirements.txt requirements-base.txt
RUN pip install -r requirements-base.txt && rm -rf /root/.cache


ENV DISABLE_CONTRACTS 1

#
#
#RUN build_deps="curl" && \
#    apt-get update && \
#    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ${build_deps} ca-certificates && \
#    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
#    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git-lfs && \
#    git lfs install && \
#    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove ${build_deps} && \
#    rm -r /var/lib/apt/lists/*
#
#
#RUN cd /project/src/duckietown-world &&  git lfs fetch  && git lfs checkout
#
