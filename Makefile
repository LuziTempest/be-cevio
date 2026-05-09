# Perintah default jika hanya mengetik 'make'
.DEFAULT_GOAL := help

# Variabel
PYTHON = venv/bin/python
PIP = venv/bin/pip
FLASK = export FLASK_APP=main.py && venv/bin/flask

.PHONY: help setup run migrate upgrade docker-up docker-down docker-logs clean

help: ## Menampilkan bantuan ini
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Install virtualenv dan dependensi
	python3 -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: ## Menjalankan server Flask secara lokal
	$(PYTHON) main.py

migrate: ## Membuat file migrasi baru (contoh: make migrate msg="tambah kolom")
	$(FLASK) db migrate -m "$(msg)"

upgrade: ## Menerapkan migrasi ke database
	$(FLASK) db upgrade

docker-up: ## Membangun dan menjalankan container Docker
	docker-compose up --build -d

docker-rebuild: ## Membangun ulang container dari nol (tanpa cache)
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

docker-down: ## Menghentikan container Docker
	docker-compose down

docker-logs: ## Melihat log dari container backend
	docker logs -f cevio-backend

docker-migrate: ## Menjalankan upgrade database di dalam Docker
	docker exec -it cevio-backend flask db upgrade

clean: ## Menghapus cache python dan folder venv
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
