.PHONY: run build

deps:
	@echo "Installing dependencies..."
	pip3 install -r requirements.txt

run: deps
	@echo "Running the application..."
	python3 main.py