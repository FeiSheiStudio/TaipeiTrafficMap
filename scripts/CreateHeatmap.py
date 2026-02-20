import folium
from folium.plugins import HeatMap
from feature_engineering import FeatureEngineering_Extend

# ----------------------------
# 2️⃣ Heatmap Generator
# ----------------------------
class Heatmap:

    def __init__(self, filename: str):
        self.filename = filename
        self.agent = FeatureEngineering_Extend(filename)
        self.df = self.agent.output  # Polars DataFrame

    def create_heatmap(self, output_html: str = "HeatmapTaipei.html"):
        # Extract valid coordinates
        heat_df = self.df.select(["lat", "lon"]).drop_nulls()
        heat_data = heat_df.to_numpy().tolist()  # Polars -> list of lists

        if not heat_data:
            raise ValueError("No valid coordinates found in the data.")

        # Create Taipei map
        taipei_center = [25.0475, 121.5170]
        m = folium.Map(location=taipei_center, zoom_start=12, tiles="cartodbpositron")

        # Add heatmap
        HeatMap(
            heat_data,
            radius=12,
            blur=15,
            min_opacity=0.3
        ).add_to(m)

        # Save HTML
        m.save(output_html)
        print(f"Heatmap successfully saved as: {output_html}")
        return m


# ----------------------------
# 3️⃣ Example usage
# ----------------------------
if __name__ == "__main__":
    filename = r"C:\Users\jarmo\Documents\Business\FeiSheStudio\Portfolio\TaipeiTrafficMap\data\combined.csv"
    heat = Heatmap(filename)
    heat.create_heatmap(r"C:\Users\jarmo\Documents\Business\FeiSheStudio\Portfolio\TaipeiTrafficMap\figures\HeatmapTaipei.html")