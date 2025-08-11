SHELL := /bin/bash

PADDLE_WHEEL_INDEX ?= https://www.paddlepaddle.org.cn/whl/linux/gpu

.PHONY: help
help:
	@echo "make validate-tasks    # Validate tasks/tasks.json and links"
	@echo "make tf-fmt            # Terraform fmt"
	@echo "make tf-validate       # Terraform validate (no backend needed)"
	@echo "make docker-build      # Build ocr-fastapi:dev image"
	@echo "make docker-build-gpu  # Build ocr-fastapi:gpu with Paddle wheel index"
	@echo "make docker-run        # Run container on :8080"
	@echo "make docker-stop       # Stop container"
	@echo "make smoke-health      # Curl /health"
	@echo "make smoke-ocr         # Curl /ocr with /etc/hosts"
	@echo "make smoke-structure   # Curl /structure with /etc/hosts"
	@echo "make smoke-extraction  # Curl /extraction with /etc/hosts"
	@echo "make smoke-batch       # Curl /ocr/batch with two /etc/hosts"
	@echo "make docker-run-gpu    # Run with --gpus all (requires NVIDIA toolkit)"
	@echo "make gpu-verify        # Run GPU container and check /health and /debug/paddle"

.PHONY: validate-tasks
tvalidate: validate-tasks

validate-tasks:
	python3 scripts/validate_tasks.py

.PHONY: tf-fmt
tf-fmt:
	cd infra/terraform && terraform fmt -recursive

.PHONY: tf-validate
tf-validate:
	cd infra/terraform && terraform validate || true

.PHONY: docker-build
docker-build:
	docker build -t ocr-fastapi:dev -f docker/Dockerfile .

.PHONY: docker-build-gpu
docker-build-gpu:
	docker build --build-arg PADDLE_WHEEL_INDEX=$(PADDLE_WHEEL_INDEX) -t ocr-fastapi:gpu -f docker/Dockerfile .

.PHONY: docker-run
docker-run:
	docker run --rm -p 8080:8080 --name ocr-api-dev ocr-fastapi:dev sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080"

.PHONY: docker-run-gpu
docker-run-gpu:
	docker run --rm --gpus all -p 8080:8080 --name ocr-api-dev ocr-fastapi:gpu sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080"

.PHONY: docker-stop
docker-stop:
	-@docker rm -f ocr-api-dev >/dev/null 2>&1 || true

.PHONY: smoke-health
smoke-health:
	curl -sS http://localhost:8080/health | jq .

.PHONY: smoke-ocr
smoke-ocr:
	curl -sS http://localhost:8080/ocr -F file=@/etc/hosts | jq .

.PHONY: smoke-structure
smoke-structure:
	curl -sS http://localhost:8080/structure -F file=@/etc/hosts | jq .

.PHONY: smoke-extraction
smoke-extraction:
	curl -sS http://localhost:8080/extraction -F file=@/etc/hosts | jq .

.PHONY: smoke-batch
smoke-batch:
	curl -sS http://localhost:8080/ocr/batch -F files=@/etc/hosts -F files=@/etc/hosts | jq .

.PHONY: gpu-verify
gpu-verify:
	@test -n "$(API_KEY)" || (echo "Set API_KEY env for auth (or unset in settings)" && exit 1)
	@echo "Starting GPU container..."
	docker run --rm --gpus all -e API_KEY=$(API_KEY) -p 8080:8080 --name ocr-api-dev ocr-fastapi:gpu sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080" & \
	sleep 3; \
	curl -sS -H "x-api-key: $(API_KEY)" http://localhost:8080/health | jq .; \
	curl -sS -H "x-api-key: $(API_KEY)" http://localhost:8080/debug/paddle | jq .; \
	docker rm -f ocr-api-dev >/dev/null 2>&1 || true
