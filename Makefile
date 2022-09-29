default: help

.PHONY: help
help:
## help: This helpful list of commands
	@echo "Usage: \n"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/-/'


.PHONY: dev
vscode:
## vscode: Install vscode extensions 
				pipenv run flask run

