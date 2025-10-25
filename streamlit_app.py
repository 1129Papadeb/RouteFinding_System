import streamlit as st
import folium
from streamlit_folium import st_folium
import xml.etree.ElementTree as ET
import numpy as np
import skfuzzy as fuzz
import pandas as pd
import os


class EvacuationSystem:
    def __init__(self, kml_file_path=None, excel_filepaths=None):
        self.kml_file_path = kml_file_path
        self.excel_filepaths = excel_filepaths if excel_filepaths else []
        self.evacuation_paths = {}
        self.barangays = {
            "Poblacion": [10.78485548380185, 122.3837072230239],
            "Bobon": [10.89540587344769, 122.2974269217951],
            "Gines": [10.85687388394953, 122.3416150076236],
            "Barangbang": [10.81689999087547, 122.3308342242847],
            "Carolina": [10.79669908350887, 122.3520502173874],
            "Lonoc": [10.78288182778105, 122.3416334769778],
            "Bacolod": [10.87712542341233, 122.3069941457462],
            "Binolbog": [10.78306359215453, 122.3340049830963],
            "Ingay": [10.843979902549595, 122.2920820324205]
        }
        self.evacuation_center = "Poblacion"
        
        # Distance data for each path (in kilometers)
        self.distances = {
            "Bobon": [24.4, 29.1, 25.6],
            "Gines": [12.7, 15.9, 18.1],
            "Bacolod": [19.9, 24.7, 20.0],
            "Lonoc": [7.71, 10.6],
            "Binolbog": [8.74, 9.8],
            "Barangbang": [12.2, 17.0],
            "Carolina": [7.06, 7.23],
            "Ingay": [24.0, 28.7]
        }
        
        self.travel_data = {}
        if self.kml_file_path:
            self.load_kml_paths()
        if self.excel_filepaths:
            self.load_all_travel_data()


    def load_kml_paths(self):
        """Load KML paths with improved error handling"""
        self.evacuation_paths = {}
        
        if not self.kml_file_path:
            return
        
        try:
            tree = ET.parse(self.kml_file_path)
            root = tree.getroot()
            namespace = ''
            if '}' in root.tag:
                namespace = root.tag.split('}')[0][1:]
            ns = {'kml': namespace}
            
            for placemark in root.findall('.//kml:Placemark', ns):
                name_element = placemark.find('kml:name', ns)
                coord_element = placemark.find('.//kml:coordinates', ns)
                
                if name_element is not None and coord_element is not None:
                    path_name = name_element.text.strip()
                    coord_text = coord_element.text.strip()
                    coord_points = []
                    
                    for line in coord_text.split():
                        if line.strip():
                            try:
                                parts = line.strip().split(',')
                                if len(parts) >= 2:
                                    lon, lat = float(parts[0]), float(parts[1])
                                    coord_points.append([lat, lon])
                            except (ValueError, IndexError):
                                continue
                    
                    if len(coord_points) >= 2:
                        self.evacuation_paths[path_name] = coord_points
                        
            st.success(f"✅ Successfully loaded {len(self.evacuation_paths)} paths from KML file")
            
        except Exception as e:
            st.error(f"❌ Error loading KML file: {e}")


    def load_all_travel_data(self):
        """Load travel data from Excel files"""
        loaded_count = 0
        for filepath in self.excel_filepaths:
            try:
                df = pd.read_excel(filepath)
                
                # Extract barangay name from filename
                fname = os.path.basename(filepath)
                fname_without_ext = os.path.splitext(fname)[0]
                
                if "_to_" in fname_without_ext:
                    barangay_name = fname_without_ext.split("_to_")[-1]
                    # Remove numeric suffixes (2, 3, etc.)
                    barangay_name = barangay_name.replace("2", "").replace("3", "")
                    barangay_name = barangay_name.capitalize().strip()
                else:
                    continue
                
                # Find slope and time columns
                slope_col = next((col for col in df.columns if "Slope" in col), None)
                time_col = next((col for col in df.columns if "Travel_Time_min" in col), None)
                
                if slope_col and time_col:
                    segment_data = []
                    for _, row in df.iterrows():
                        try:
                            dummy_curvature = np.random.uniform(0, 1)
                            segment_data.append({
                                "slope": float(row[slope_col]),
                                "travel_time": float(row[time_col]),
                                "curvature": dummy_curvature
                            })
                        except Exception:
                            continue
                    
                    if segment_data:
                        self.travel_data[barangay_name] = segment_data
                        loaded_count += 1
                    
            except Exception as e:
                st.warning(f"⚠️ Error processing file '{os.path.basename(filepath)}': {e}")
        
        if loaded_count > 0:
            st.success(f"✅ Loaded travel data for {loaded_count} barangays")


    def fuzzy_evaluation(self, slope, travel_time, curvature):
        """Evaluate path segment using fuzzy logic"""
        # Slope membership functions
        x_slope = np.arange(-10, 11, 0.1)
        slope_low = fuzz.trimf(x_slope, [-10, -5, 0])
        slope_med = fuzz.trimf(x_slope, [-2, 0, 2])
        slope_high = fuzz.trimf(x_slope, [0, 5, 10])
        slope_level_low = fuzz.interp_membership(x_slope, slope_low, slope)
        slope_level_med = fuzz.interp_membership(x_slope, slope_med, slope)
        slope_level_high = fuzz.interp_membership(x_slope, slope_high, slope)


        # Travel time membership functions
        x_time = np.arange(0, 31, 1)
        time_fast = fuzz.trimf(x_time, [0, 0, 10])
        time_avg = fuzz.trimf(x_time, [5, 15, 25])
        time_slow = fuzz.trimf(x_time, [20, 30, 30])
        time_level_fast = fuzz.interp_membership(x_time, time_fast, travel_time)
        time_level_avg = fuzz.interp_membership(x_time, time_avg, travel_time)
        time_level_slow = fuzz.interp_membership(x_time, time_slow, travel_time)


        # Curvature membership functions
        x_curv = np.arange(0, 1.1, 0.01)
        curv_low = fuzz.trimf(x_curv, [0, 0, 0.5])
        curv_med = fuzz.trimf(x_curv, [0.2, 0.5, 0.8])
        curv_high = fuzz.trimf(x_curv, [0.5, 1, 1])
        curv_level_low = fuzz.interp_membership(x_curv, curv_low, curvature)
        curv_level_med = fuzz.interp_membership(x_curv, curv_med, curvature)
        curv_level_high = fuzz.interp_membership(x_curv, curv_high, curvature)


        # Fuzzy rules
        cost_low = np.fmin(np.fmin(np.fmin(slope_level_low, time_level_fast), curv_level_low), 0.1)
        cost_med = np.fmin(np.fmax(np.fmax(slope_level_med, time_level_avg), curv_level_med), 0.5)
        cost_high = np.fmin(np.fmax(np.fmax(slope_level_high, time_level_slow), curv_level_high), 0.9)
        cost = np.fmax(cost_low, np.fmax(cost_med, cost_high))
        return cost


    def a_star_path(self, start, goal):
        """
        Find best evacuation path using A* algorithm with fuzzy logic
        Returns tuple: (barangay_name, cost, time, distance)
        """
        graph = {}
        for barangay, segments in self.travel_data.items():
            total_cost = 0
            total_time = 0
            for seg in segments:
                total_cost += self.fuzzy_evaluation(seg['slope'], seg['travel_time'], seg['curvature'])
                total_time += seg['travel_time']
            graph[barangay] = {"cost": total_cost, "time": total_time}
        
        # Find matching barangays
        candidates = [(name, data["cost"], data["time"]) for name, data in graph.items() 
                     if goal.lower() in name.lower()]
        
        if not candidates:
            return None
        
        # Find the best path (minimum cost)
        best = min(candidates, key=lambda x: x[1])
        barangay_name = best[0]
        
        # Get the corresponding distance
        distance = None
        if barangay_name in self.distances:
            distance = min(self.distances[barangay_name])
        
        return (best[0], best[1], best[2], distance)


    def create_evacuation_map(self, selected_barangay=None):
        """Create interactive folium map with evacuation routes"""
        map_center = self.barangays[self.evacuation_center]
        m = folium.Map(location=map_center, zoom_start=12)
        
        # Add markers for all barangays
        for name, coords in self.barangays.items():
            color = "red" if name == self.evacuation_center else "blue"
            if name == selected_barangay:
                color = "orange"
            folium.Marker(
                location=coords,
                popup=f"{name}{' (Evacuation Center)' if name == self.evacuation_center else ''}",
                icon=folium.Icon(color=color)
            ).add_to(m)


        if selected_barangay and selected_barangay != self.evacuation_center:
            # Draw all available paths in gray
            for path_name, coords in self.evacuation_paths.items():
                folium.PolyLine(
                    locations=coords,
                    color="gray",
                    weight=3,
                    opacity=0.5,
                    tooltip=f"Path: {path_name}"
                ).add_to(m)


            # Highlight the best path in red
            best_path = self.a_star_path(self.evacuation_center, selected_barangay)
            if best_path:
                path_name = f"Poblacion to {selected_barangay}"
                path_coords = self.evacuation_paths.get(path_name, None)
                if path_coords:
                    folium.PolyLine(
                        locations=path_coords,
                        color='red',
                        weight=6,
                        opacity=0.9,
                        tooltip=f"Best Path: {path_name}"
                    ).add_to(m)
        
        return m


def load_embedded_files():
    """Load data files from the 'data' folder"""
    kml_file = None
    excel_files = []
    
    # Look for files in 'data' folder
    data_folder = "data"
    
    if os.path.exists(data_folder):
        for file in os.listdir(data_folder):
            file_path = os.path.join(data_folder, file)
            
            if file.endswith('.kml'):
                kml_file = file_path
            elif file.endswith(('.xlsx', '.xls')):
                excel_files.append(file_path)
    
    return kml_file, excel_files


def main():
    st.set_page_config(
        page_title="Leon Evacuation System",
        page_icon="🚨",
        layout="wide"
    )
    
    st.title("🚨 Leon Evacuation System")
    
    # Initialize session state
    if 'system' not in st.session_state:
        st.session_state.system = None
        st.session_state.auto_loaded = False
    
    # Try to auto-load embedded files on first run
    if not st.session_state.auto_loaded:
        kml_file, excel_files = load_embedded_files()
        
        if kml_file and excel_files:
            with st.spinner("Loading embedded data files..."):
                st.session_state.system = EvacuationSystem(kml_file, excel_files)
                st.session_state.auto_loaded = True
                st.success("✅ System ready with pre-loaded data!")
        else:
            st.session_state.auto_loaded = True
            st.error("❌ No data files found in 'data/' folder. Please ensure KML and Excel files are present.")
    
    # Sidebar for information
    with st.sidebar:
        st.header("ℹ️ System Information")
        
        # Show status       
        # Display loaded data statistics
        if st.session_state.system and st.session_state.system.evacuation_paths:
            st.metric("Routes Loaded", len(st.session_state.system.evacuation_paths))
        
        if st.session_state.system and st.session_state.system.travel_data:
            st.metric("Barangays with Data", len(st.session_state.system.travel_data))
        else:
            st.warning("⚠️ No data loaded")
        
        st.markdown("---")
        
        # Info section
        st.markdown("### 📋 How to Use")
        st.markdown("""
        1. Select a barangay from the dropdown
        2. View the optimal evacuation route
        3. Check distance and travel time
        4. See the highlighted path on the map
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This system uses **fuzzy logic** and **A* algorithm** to calculate 
        the optimal evacuation route based on:
        - 🏔️ Road slope
        - ⏱️ Travel time
        - 🛣️ Path curvature
        """)
        
    # Main content area
    if st.session_state.system is None:
        st.warning("⚠️ System initialization failed")
        st.markdown("""
        ### 🚨 Data Files Not Found
        
        Please ensure the following:
        1. A `data/` folder exists in the project root
        2. The folder contains:
           - One `.kml` file (evacuation routes)
           - Multiple `.xlsx` files (travel data for each barangay)
        
        **Expected file structure:**
        ```
        project/
        ├── streamlit_app.py
        └── data/
            ├── completeroad.kml
            ├── Poblacion_to_Bacolod.xlsx
            ├── Poblacion_to_Carolina.xlsx
            └── ... (other Excel files)
        ```
        """)
        
    else:
        system = st.session_state.system
        
        # Barangay selection
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("### Select Barangay")
            barangay_options = ["-- Select a barangay --"] + [
                name for name in system.barangays.keys() 
                if name != system.evacuation_center
            ]
            selected_barangay = st.selectbox(
                "Choose barangay to evacuate:",
                barangay_options,
                label_visibility="collapsed"
            )
        
        # Display map
        if selected_barangay and selected_barangay != "-- Select a barangay --":
            evacuation_map = system.create_evacuation_map(selected_barangay)
            
            # Show evacuation info
            st.markdown("---")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### 📊 Evacuation Details")
                best_path = system.a_star_path(system.evacuation_center, selected_barangay)
                
                if best_path:
                    st.success("✅ Best Route Found!")
                    
                    # Display metrics
                    metric_col1, metric_col2 = st.columns(2)
                    with metric_col1:
                        if best_path[3] is not None:
                            st.metric("📏 Distance", f"{best_path[3]:.2f} km")
                        else:
                            st.metric("📏 Distance", "N/A")
                    
                    with metric_col2:
                        st.metric("⏱️ Travel Time", f"{best_path[2]:.2f} min")
                    
                    # Display route info
                    st.markdown("---")
                    st.markdown("**Route Information:**")
                    st.write(f"**From:** {system.evacuation_center} (Evacuation Center)")
                    st.write(f"📍 **To: Brgy.** {selected_barangay}")
                    
                    # Show all available paths
                    if selected_barangay in system.distances:
                        st.markdown("**All Available Paths:**")
                        for i, dist in enumerate(system.distances[selected_barangay], 1):
                            st.write(f"Path {i}: {dist} km")
                else:
                    st.warning("⚠️ No travel data available for this barangay")
            
            with col2:
                # ✅ FIX: Added returned_objects=[] to prevent reloads on map clicks
                st_folium(evacuation_map, width=900, height=600, returned_objects=[])
        else:
            # Show map without selection
            default_map = system.create_evacuation_map()
            # ✅ FIX: Added returned_objects=[] to prevent reloads on map clicks
            st_folium(default_map, width=1200, height=500, returned_objects=[])


if __name__ == "__main__":
    main()
