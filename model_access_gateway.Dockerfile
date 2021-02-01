# Import an docker image with python and conda preinstalled
FROM continuumio/miniconda3

WORKDIR /app

# Create the conda environment by using the supplied requirements file
COPY model_access_gateway/requirements.yml requirements.yml
RUN conda env create -f requirements.yml

# Copy all required python scripts
COPY common_data_access common_data_access
COPY model_access_gateway model_access_gateway
COPY run.py .

# Active conda to use the right environment
RUN echo "source activate model-access-gateway" > ~/.bashrc
ENV PATH /opt/conda/envs/model-access-gateway/bin:$PATH

EXPOSE 5001

# Set the env such that the "flask" command works inside the container
# This way a developer can execute flask commands when using "docker exec -it <container_id>"
ENV FLASK_APP=model_access_gateway/src/__init__.py

# Set entrypoint for docker
ENTRYPOINT ["python", "run.py", "gateway"]