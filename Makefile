compile-requirements:
	pip-compile --no-emit-index-url --no-header

pre-commit:
	pre-commit run -a

rebuild:
	python build_readme.py
