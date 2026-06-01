.PHONY: test demo service-demo ssh-demo app lint

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

demo:
	PYTHONPATH=src python -m ubuntuops.cli diagnose --issue "ssh login attempts are high" --auth-log samples/auth.log --output-dir reports

service-demo:
	PYTHONPATH=src python -m ubuntuops.cli service nginx --journal-file samples/journal_nginx_failed.log

ssh-demo:
	PYTHONPATH=src python -m ubuntuops.cli ssh --log samples/auth.log

app:
	streamlit run app.py

lint:
	ruff check src tests
