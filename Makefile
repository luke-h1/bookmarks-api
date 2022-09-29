default: help

.PHONY: help
help:
## help: This helpful list of commands
	@echo "Usage: \n"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/-/'


.PHONY: dev
dev:
				pipenv run flask run

.PHONY: db-up
db-up:
				docker-compose up

.PHONY: db-init 
db-init: 
				pipenv run flask db init

.PHONY: db-upgrade 
db-upgrade: 
				pipenv run flask db upgrade


.PHONY: db-migrate
db-migrate: 
				pipenv run flask db migrate
