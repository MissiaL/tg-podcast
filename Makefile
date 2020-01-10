push:
	docker-compose run app python main.py pull
	docker-compose run app python main.py push

clean_storage:
	docker-compose run app python main.py clean