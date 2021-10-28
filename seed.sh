## Seeding ##
# (1) find container id (2) run command inside the container
# main
docker exec -it $(docker ps -aqf "name=model-sharing-backend") flask seed-db
docker exec -it $(docker ps -aqf "name=ingredient-service") flask seed-db

docker exec -it $(docker ps -aqf "name=model-sharing-backend") flask cache-om

# taste/nutrition
docker exec -it $(docker ps -aqf "name=tomato-saltiness-model-access-gateway") flask seed-db
docker exec -it $(docker ps -aqf "name=sweet-sourness-model-access-gateway") flask seed-db
docker exec -it $(docker ps -aqf "name=nutrition-model-access-gateway") flask seed-db
docker exec -it $(docker ps -aqf "name=ingredient-access-gateway") flask seed-db
docker exec -it $(docker ps -aqf "name=recipe-access-gateway") flask seed-db

#pasteurization/shelflife
docker exec -it $(docker ps -aqf "name=pasteurization-model-access-gateway") flask seed-db
docker exec -it $(docker ps -aqf "name=shelflife-model-access-gateway") flask seed-db
docker exec -it $(docker ps -aqf "name=microbe-hex-access-gateway") flask seed-db

