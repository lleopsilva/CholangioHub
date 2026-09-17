PROJECT_NAME=cholangiohub


COMPOSE_FILE=infrastructure/docker/compose/docker-compose.yml



help:
	@echo ""
	@echo "CholangioHub commands"
	@echo ""
	@echo "make install       - install python dependencies"
	@echo "make infra-up      - start docker infrastructure"
	@echo "make infra-down    - stop docker infrastructure"
	@echo "make infra-status  - check containers"
	@echo "make infra-logs    - show logs"
	@echo "make migrate       - apply database migrations"
	@echo "make test          - run tests"
	@echo ""



install:
	uv sync



infra-up:
	docker compose \
	-f $(COMPOSE_FILE) \
	up -d



infra-down:
	docker compose \
	-f $(COMPOSE_FILE) \
	down



infra-status:
	docker compose \
	-f $(COMPOSE_FILE) \
	ps



infra-logs:
	docker compose \
	-f $(COMPOSE_FILE) \
	logs -f



migrate:
	uv run python scripts/apply_migrations.py



test:
	uv run pytest