email ?= me@example.com
domain ?= example.com
region ?= us-east-1

.build: Dockerfile update.py
	@docker-compose build renewcert
	@touch .build

shell: .build
	@docker-compose run --rm --entrypoint sh renewcert

run: .build
	@docker-compose run --rm \
		-e EMAIL=$(email) \
		-e DOMAIN=$(domain) \
		-e AWS_REGION=$(region) \
		renewcert
