FROM openjdk:17-slim

# ps command
RUN apt-get update && apt-get install -y procps

# Install build dependencies
RUN apt-get install -y \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl

# Download and install Python 3.10.0
RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz && \
    tar xzf Python-3.10.0.tgz && \
    cd Python-3.10.0 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.10.0 Python-3.10.0.tgz

# Update alternatives to make Python 3.10 the default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.10 1 && \
    update-alternatives --set python3 /usr/local/bin/python3.10

# Install pip for Python 3.10
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py

# Add MySQL JDBC driver
ENV JDBC_DRIVER_VERSION=8.0.30
RUN wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/${JDBC_DRIVER_VERSION}/mysql-connector-java-${JDBC_DRIVER_VERSION}.jar -P /opt/spark/jars/

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "producer.py"]

