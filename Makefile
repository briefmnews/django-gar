clean:
	rm -rf *.egg-info .pytest_cache
	rm -rf htmlcov
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

coverage:
	pytest --cov=django_gar tests

report:
	pytest --cov=django_gar --cov-report=html tests

install:
	pip install -r test_requirements.txt

release:
	git tag -a $(shell python -c "from django_gar import __version__; print(__version__)") -m "$(m)"
	git push origin --tags
