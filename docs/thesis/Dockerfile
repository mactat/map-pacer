FROM ubuntu:focal

RUN ln -snf /usr/share/zoneinfo/Etc/UTC /etc/localtime \
    && echo "Etc/UTC" > /etc/timezone \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-xetex \
        texlive-fonts-recommended \
        latexmk \
        xzdec \
        build-essential \
        wget
RUN apt-get install -y texmaker
RUN apt-get install -y texlive-bibtex-extra
RUN apt-get install -y texlive-science
RUN apt-get -y install biber
# RUN tlmgr init-usertree && tlmgr update --self && tlmgr install biblatex
WORKDIR /data