## Seeding ##
# (1) find container id (2) run command inside the container
docker exec -it $(docker ps -aqf "name=ingredient-service") flask seed-db
docker exec -it $(docker ps -aqf "name=tomato-saltiness-model-access-gateway") flask seed-db
docker exec -it $(docker ps -aqf "name=sweet-sourness-model-access-gateway") flask seed-db
docker exec -it $(docker ps -aqf "name=nutrition-model-access-gateway") flask seed-db
docker exec -it $(docker ps -aqf "name=model-sharing-backend") flask seed-db
docker exec -it $(docker ps -aqf "name=model-sharing-backend") flask cache-om
