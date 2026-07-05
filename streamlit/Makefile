.PHONY: help install pipeline analyses dashboard db-load clean

help:
	@echo "Commandes disponibles :"
	@echo "  make install    - Installer les dépendances Python"
	@echo "  make pipeline   - Lancer le pipeline Bronze/Silver/Gold"
	@echo "  make analyses   - Lancer les analyses (ruptures, clustering, corrélation)"
	@echo "  make dashboard  - Lancer le dashboard Streamlit"
	@echo "  make db-load    - Charger data/gold/ dans PostgreSQL"
	@echo "  make clean      - Nettoyer données dérivées (bronze/silver/gold)"

install:
	pip install -r requirements.txt

pipeline:
	python pipeline.py

analyses:
	python analyses/ruptures_detection.py
	python analyses/clustering_chaines.py
	python analyses/correlation_themes_parite.py

dashboard:
	streamlit run dashboard/app.py

db-load:
	python backend/load_gold_to_postgres.py

clean:
	rm -rf data/bronze/* data/silver/* data/gold/* logs/*.log
	@echo "Couches dérivées nettoyées. Relancer 'make pipeline' pour regénérer."
