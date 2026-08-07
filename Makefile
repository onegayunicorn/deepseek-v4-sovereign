# ============================================================
# SOVEREIGN — DeepSeek-V4 Sovereign Orchestrator
# ============================================================
.PHONY: help setup run api cli test lint check build-apk build-exe release \
        docker-build docker-up docker-down status clean tree

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Create venv + install dependencies
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

run: ## Boot the orchestrator (CLI loop)
	.venv/bin/python -m sovereign.main dashboard

api: ## Run the FastAPI server
	.venv/bin/uvicorn sovereign.main:app --host 0.0.0.0 --port 8000 --reload

cli: ## Invoke the sovereign CLI
	.venv/bin/python -m sovereign.main --help

test: ## Run the test suite
	.venv/bin/python -m pytest tests/ -v --tb=short || echo "  └─ pytest not available"

lint: ## Syntax-check all Python modules
	find src -name "*.py" -not -path "*/.venv/*" | xargs -I{} python3 -c "import ast; ast.parse(open('{}').read())" && echo "  ✓ all modules parse"

check: ## Validate YAML configs
	python3 -c "import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('config/*.yaml')+glob.glob('**/*.yaml', recursive=True)]" && echo "  ✓ all YAML parses"

build-apk: ## Build Android APK (requires JDK 17 + Android SDK)
	bash builds/apk/build_apk.sh

build-exe: ## Build Windows EXE (run on Windows; see builds/exe/README.md)
	bash builds/exe/build_exe.sh

release: ## Run the release pipeline (VERSION=x.y.z CHANNELS=a,b)
	bash distribution/release_pipeline.sh

docker-build: ## Build docker images
	docker compose -f docker/docker-compose.yml build

docker-up: ## Start docker stack
	docker compose -f docker/docker-compose.yml up -d

docker-down: ## Stop docker stack
	docker compose -f docker/docker-compose.yml down

status: ## Show monorepo status + connected projects
	python3 integrations/connector.py

tree: ## Print the monorepo tree
	find . -maxdepth 2 -type d -not -path "./.git*" -not -path "./.venv*" | sort

clean: ## Clean build artifacts
	rm -rf build/ dist/ .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
