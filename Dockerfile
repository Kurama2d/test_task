FROM odoo:16

RUN pip3 install --upgrade pip

RUN pip3 install celery redis

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
