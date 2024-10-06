requirements.txt: requirements.in uv
	./uv pip compile requirements.in -o requirements.txt

.venv/bin/activate:
	./uv venv

.PHONY: sync
sync: .venv/bin/activate requirements.txt
	./uv pip sync requirements.txt

rebuild: sync
	./uv run python build_readme.py

pre-commit: sync
	./uv run pre-commit run -a
