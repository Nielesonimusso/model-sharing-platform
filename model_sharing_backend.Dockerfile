# Import an docker image with python and conda preinstalled
FROM continuumio/miniconda3

WORKDIR /app

# Create the conda environment by using the supplied requirements file
COPY model_sharing_backend/requirements.yml requirements.yml
COPY unit-translation-component ../unit-translation-component
RUN conda env create -f requirements.yml

# Copy all required python scripts
COPY common_data_access common_data_access
COPY model_sharing_backend model_sharing_backend
COPY run.py .

# Install and start redis for the unit translation component
RUN apt-get update -q && apt-get -yq install redis

# Active conda to use the right environment
RUN echo "source activate model-sharing-platform" > ~/.bashrc
ENV PATH /opt/conda/envs/model-sharing-platform/bin:$PATH

EXPOSE 5000

# Set the env such that the "flask" command works inside the container
# This way a developer can execute flask commands when using "docker exec -it <container_id>"
ENV FLASK_APP=model_sharing_backend/src/__init__.py

# Set entrypoint for docker
RUN echo "#!/bin/bash" > entry.sh
RUN echo "redis-server --daemonize yes" >> entry.sh
RUN echo "python run.py backend" >> entry.sh
RUN chmod +x entry.sh
ENTRYPOINT ["/app/entry.sh"]
