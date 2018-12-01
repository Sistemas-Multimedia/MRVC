export_package:
	python setup.py install

install_deps:
	pip install -r requirements.txt

perform_tests:		install_dependencies
	make -C tests all

all:	install_dependencies create_documentation perform_tests

info:
	@echo Please, select between:
	@echo "  \033[0;31mexport_package\033[0m (install the 'mcdwt' package in Disutils)"
	@echo "  \033[0;31minstall_deps\033[0m (install Python dependencies)"
	@echo "  \033[0;31mperform_tests\033[0m (run the test scripts)"

default: info

