.PHONY: help install test demo verify clean docker-build

help:
	@echo "Claude4RPM - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install Python dependencies"
	@echo "  test          - Run unit tests"
	@echo "  demo          - Run demonstration"
	@echo "  verify        - Verify installation"
	@echo "  clean         - Clean output and cache files"
	@echo "  docker-build  - Build Docker image"
	@echo "  help          - Show this help message"

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

demo:
	./demo.py

verify:
	./verify.sh

clean:
	rm -rf output/*
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
	rm -f *.log
	rm -rf .pytest_cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

docker-build:
	cd docker && docker build -t claude4rpm-builder .

docker-test:
	docker run -it --rm claude4rpm-builder /bin/bash -c "rpmbuild --version && go version"
