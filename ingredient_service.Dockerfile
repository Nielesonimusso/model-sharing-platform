# Import an docker image with python and conda preinstalled
FROM continuumio/miniconda3

WORKDIR /app

# Create the conda environment by using the supplied requirements file
COPY ingredient_data_service/requirements.yml requirements.yml
RUN conda env create -f requirements.yml

# Copy all required python scripts
COPY common_data_access common_data_access
COPY ingredient_data_service ingredient_data_service
COPY run.py .

# Active conda to use the right environment
RUN echo "source activate ingredient-data-service" > ~/.bashrc
ENV PATH /opt/conda/envs/ingredient-data-service/bin:$PATH

EXPOSE 5002

# Set the env such that the "flask" command works inside the container
# This way a developer can execute flask commands when using "docker exec -it <container_id>"
ENV FLASK_APP=ingredient_data_service/src/__init__.py

# Set entrypoint for docker
ENTRYPOINT ["python", "run.py", "ingredient_service"]