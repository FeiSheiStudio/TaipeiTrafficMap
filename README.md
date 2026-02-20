# Taipei Traffic Accident Heatmap

This project started as a small experiment in **data preprocessing with Polars** and evolved into an **interactive heatmap of traffic accidents in Taipei**.

It demonstrates efficient data processing, address and time extraction, and visualization of spatial data.

---

## Features

- **Data Preprocessing with Polars**: Fast and efficient handling of large datasets.  
- **Address Extraction**: Parses accident locations into district, road, section, lane, and more.  
- **Time Extraction**: Converts timestamps into year, month, week, and day for analysis.  
- **Distance Calculation**: Computes distances from Taipei Main Station.  
- **Interactive Heatmap**: Uses Folium to generate a zoomable, pan-able heatmap of accident locations.

---

## Project Structure

### Scripts

- `feature_engineering.py` — Handles data cleaning and feature extraction  
- `create_heatmap.py` — Generates the heatmap  

### Data

- `combined.csv` — Accident data CSV (sample or full)  

### Root

- `README.md`  
- `requirements.txt`  
- `.gitignore`  

---

## Requirements

- Python 3.10+  
- `polars`  
- `numpy`  
- `folium`  

Install dependencies with `pip install -r requirements.txt`.

---

## Usage

1. Place your accident CSV in the `data/` folder (or update the path in `create_heatmap.py`).  
2. Run the heatmap script with `python scripts/create_heatmap.py`.  
3. The interactive heatmap will be saved as `HeatmapTaipei.html`.  
4. Open the HTML file in a browser to explore accident hotspots across Taipei.

---

## Example Output

- Heatmap centered on Taipei  
- Hotspots indicate areas with higher accident density  
- Fully interactive: zoom, pan, and explore clusters  

<img width="1630" height="983" alt="image" src="https://github.com/user-attachments/assets/cf98b494-dc5e-48d1-a26e-08cab33be0d1" />



---

## Notes

- Focused on **showcasing Polars for fast preprocessing**.  
- CSV must include `lat` and `lon` columns.  
- The pipeline handles inconsistent date formatting and cleans location strings automatically.  
- The heatmap is built entirely with **Folium**, producing a shareable HTML file.

---

## Author

**蔡竹飛**  

Created as a portfolio project to demonstrate:  
- Data preprocessing and cleaning with **Polars**  
- Handling real-world messy CSVs  
- Geospatial visualization and heatmap generation with **Folium**  
- Python scripting and workflow organization for data projects
