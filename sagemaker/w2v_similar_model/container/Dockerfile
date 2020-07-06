FROM python:3.7

ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=42

WORKDIR /opt/program

COPY Pipfile Pipfile.lock /opt/program/

RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         nginx \
         ca-certificates \
    && rm -rf /var/lib/apt/lists/*


#RUN pip3 install --user pipenv \
RUN pip install pipenv
#RUN pipenv install --system
#RUN pipenv lock && pipenv install --system --deploy --ignore-pipfile
RUN pipenv lock && pipenv install --system --ignore-pipfile

# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"
ENV MODEL_PATH="/opt/ml/model"


# env for endpoint server
ENV MODEL_SERVER_TIMEOUT=60
# default is num of cpu
#ENV MODEL_SERVER_WORKERS=2

# Set up the program in the image
COPY w2v_similar /opt/program
WORKDIR /opt/program

