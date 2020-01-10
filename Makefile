push:
	docker-compose run app python main.py pull
	docker-compose run app python main.py push

clear_storage:
	docker-compose run app python main.py clean