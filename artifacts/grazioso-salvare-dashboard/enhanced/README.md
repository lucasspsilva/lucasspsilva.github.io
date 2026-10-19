# Grazioso Salvare Dashboard

A Dash dashboard that shows shelter animals from MongoDB and lets you search
by Animal ID or Name using binary search.

## Requirements
- Python 3
- MongoDB running locally on `localhost:27017`

## Setup
Install the packages:
```
pip install pymongo dash dash-leaflet pandas matplotlib pytest jupyter
```

Load the 500 sample records into MongoDB:
```
python seed_data.py
```

## Run
Open `ProjectTwoDashboard.ipynb` in Jupyter and run the cell:
```
jupyter notebook ProjectTwoDashboard.ipynb
```
The dashboard appears below the cell (or at http://127.0.0.1:8050).

## Tests
```
python -m pytest tests
```
