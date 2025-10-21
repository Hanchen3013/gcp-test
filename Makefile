.PHONY: help install test lint clean deploy run

help:
	@echo "GCP Data Pipeline - Available Commands"
	@echo "======================================="
	@echo "make install       - Install dependencies"
	@echo "make test          - Run tests"
	@echo "make lint          - Run linting"
	@echo "make clean         - Clean build artifacts"
	@echo "make deploy        - Deploy to GCP"
	@echo "make run           - Run example pipeline"
	@echo "make setup-venv    - Create virtual environment"

setup-venv:
	python3 -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

install:
	pip install -e .
	pip install -r requirements.txt

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-coverage:
	pytest --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/ --max-line-length=100 --exclude=venv,__pycache__
	black --check src/ tests/

format:
	black src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/

deploy:
	@echo "Deploying to GCP..."
	@./deploy.sh

run:
	@echo "Running example pipeline..."
	python examples/basic_pipeline.py

run-advanced:
	@echo "Running advanced pipeline example..."
	python examples/advanced_pipeline.py

# Run main pipeline with example data
run-main:
	python main.py --source examples/sample_data.json --source-type file --add-timestamp

# Terraform commands
tf-init:
	cd terraform && terraform init

tf-plan:
	cd terraform && terraform plan

tf-apply:
	cd terraform && terraform apply

tf-destroy:
	cd terraform && terraform destroy

# Documentation
docs:
	@echo "Opening README.md..."
	@cat README.md
