cluster-0-up:
	docker-compose --env-file redis0.env up
cluster-1-up:
	docker-compose --env-file redis1.env up
