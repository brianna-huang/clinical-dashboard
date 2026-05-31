setup:
	pip install -r requirements.txt

pipeline:
	mkdir -p outputs
	python load_data.py
	python init_analysis.py
	python statistical_analysis.py
	python subset_analysis.py

dashboard:
	streamlit run dashboard.py