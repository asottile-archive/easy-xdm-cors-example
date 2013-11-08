test: py_env
	bash -c 'source py_env/bin/activate && \
		testify tests -x selenium'
		
test_selenium: py_env
	bash -c 'source py_env/bin/activate && \
		testify tests.selenium'

test_selenium_no_ie: py_env
	bash -c 'source py_env/bin/activate && \
		testify tests.selenium -x internet-explorer'
		
py_env: requirements.txt
	rm -rf py_env
	virtualenv py_env --system-site-packages
	bash -c 'source py_env/bin/activate && \
		pip install -r requirements.txt'

clean:
	rm -rf py_env
