init:
	cp .default.env .env
debug:
	python -m debugpy --listen 5678 insightbeam
run:
	python insightbeam

before-precommit:
	echo "\033[35m== Starting precommit Formatting and analysis... ==\033[0m"

after-precommit:
	echo "\033[35m== finished precommit Formatting and analysis... ==\033[0m"

precommit: before-precommit sort format lint static-analysis after-precommit

format:
	echo "\033[92m==> Formatting Code! ==>\033[0m"
	python -m black insightbeam 

lint:
	echo "\033[92m==> Linting Code! ==>\033[0m"
	flake8 --max-line-length 120 insightbeam

static-analysis:
	echo "\033[92m==> Statically Analyzing Code! ==>\033[0m"
	mypy insightbeam | echo "done"

sort:
	echo "\033[92m==> Sorting Imports! ==>\033[0m"
	python -m isort insightbeam