test:
	rm -rf py_env
	virtualenv py_env --system-site-packages
	bash -c 'source py_env/bin/activate && \
		pip install -r requirements.txt --upgrade && \
		testify tests -x selenium'
		
test_selenium:
	rm -rf py_env
	virtualenv py_env --system-site-packages
	bash -c 'source py_env/bin/activate && \
		pip install -r requirements.txt && \
		testify tests.selenium'
		
coverage:
	virtualenv py_env --system-site-packages
	bash -c 'source py_env/bin/activate && \
		pip install -r requirements.txt && \
		coverage erase && \
		coverage run fix_coverage.py'		
		