#!/bin/bash

service_directories=(ingredient_data_service model_access_gateway model_sharing_backend)

for d in "${service_directories[@]}"
do
  cd $d || exit
  conda env update -f requirements.yml
  cd ..
done