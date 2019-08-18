FROM dev/centos

#LABEL name="CentOS Base Image" \
#    vendor="CentOS" \
#    license="GPLv2" \
#    build-date="20170911"

# WeasyPrint
RUN yum install -y redhat-rpm-config \
    && yum install -y python-cffi \
    && yum install -y libffi-devel \
    && yum install -y cairo \
    && yum install -y pango \
    && yum install -y gdk-pixbuf2 \
    && yum -y clean all

COPY requirements.txt /root/
RUN cd /root \
    && pip3 install -r requirements.txt \
    && rm -f requirements.txt

ENV TZ=Asia/Shanghai
WORKDIR /workspace

#COPY entrypoint.sh /usr/local/bin/
#RUN chmod 755 /usr/local/bin/entrypoint.sh
#ENTRYPOINT ["entrypoint.sh"]

CMD ["/bin/bash"]
