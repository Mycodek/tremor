VENV := venv
PORT := 8000

.PHONY: bootstrap run clean

bootstrap:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

run:
	$(VENV)/bin/streamlit run main.py --server.address 0.0.0.0 --server.port $(PORT)

clean:
	rm -rf $(VENV) __pycache__ .streamlit
