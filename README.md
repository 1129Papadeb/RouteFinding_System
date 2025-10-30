# 🚨 SAFE Route

An intelligent evacuation route planning system using **A* pathfinding algorithm** and **fuzzy logic** to determine optimal evacuation paths in Leon, Iloilo, Philippines.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg) ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Data Requirements](#data-requirements)
- [Algorithm Details](#algorithm-details)
- [Screenshots](#screenshots)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

The SAFE Route (Smart Alert and Fast Evacuation with Rerouting Technology) is a web-based application aiding emergency responders and local government units in planning optimal evacuation routes during disasters in Leon, Iloilo. The system utilizes advanced pathfinding algorithms combined with real-world road conditions to recommend the safest and most efficient evacuation paths.

---

## ✨ Features

### 🗺️ Interactive Map Visualization

- Satellite imagery powered by Esri
- Visual markers for all barangays (villages)
- Color-coded path highlighting (gray for alternatives, red for optimal)
- Interactive route selection and map navigation

### 🧠 Intelligent Pathfinding

- Optimized **A* Algorithm** using priority queues
- \(g(n)\): Actual fuzzy logic-derived cost from start to node \(n\)
- \(h(n)\): Heuristic cost estimated by Haversine distance to the goal
- \(f(n) = g(n) + h(n)\): Total cost guiding optimal path search

### 📊 Fuzzy Logic Evaluation

Road segments evaluated based on:

- **Slope**: Low (-10 to 0°), Medium (-2 to 2°), High (0 to 10°)
- **Travel Time**: Fast (0–10 mins), Average (5–25 mins), Slow (20–30 mins)
- **Curvature**: Low (0–0.5), Medium (0.2–0.8), High (0.5–1)

### 📈 Results Dashboard

- Total distance in kilometers
- Estimated travel time in minutes
- Composite cost metrics
- Alternative routes display

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Internet connection (for map tiles)

### Steps

git clone https://github.com/yourusername/leon-evacuation-system.git
cd leon-evacuation-system
pip install -r requirements.txt
streamlit run streamlit_app.py

Alternatively, install dependencies manually:

pip install streamlit folium streamlit-folium numpy scikit-fuzzy pandas openpyxl


---

## 📖 Usage

- Launch the app.
- View all barangays mapped.
- Select a barangay to evacuate.
- Observe the optimal path highlighted.
- Review distance, travel time, and costs.
- Change barangay selections to explore alternatives.

---

## 📁 Data Requirements

### KML Files

- Must contain placemarks with route names and coordinate arrays
- Format: `longitude,latitude,altitude`

### Excel Travel Data

- Required columns: **Slope**, **Travel_Time_min**
- Filename format: `Poblacion_to_[BarangayName].xlsx`

---

## 🧮 Algorithm Details

### A* Pathfinding

A* finds an optimal path with cost function:

\[
f(n) = g(n) + h(n)
\]

- \(g(n)\): Actual fuzzy-evaluated cost to node \(n\)
- \(h(n)\): Heuristic Haversine distance to goal

The search explores nodes prioritizing minimal \(f(n)\) values.

### Fuzzy Logic

- Uses triangular membership functions to fuzzify inputs.
- Combines fuzzy rules via AND/OR operators.
- Defuzzifies to yield crisp segment costs.

### Haversine Formula

\[
distance = 2 R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \text{lat}}{2}\right) + \cos(\text{lat}_1) \cos(\text{lat}_2) \sin^2\left(\frac{\Delta \text{lon}}{2}\right)} \right)
\]

Where \(R = 6371\, km\).

---

## 📸 Screenshots

- Main interactive map interface
- Evacuation path selection
- Results dashboard with route metrics

---

## ⚙️ Requirements

### Hardware

- Minimum: Intel Core i3, 4GB RAM, 500MB storage
- Recommended: Intel Core i5, 8GB RAM, 1GB storage

### Software

- OS: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- Python 3.8+
- Supported browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### Libraries

streamlit >= 1.28.0
folium >= 0.14.0
streamlit-folium >= 0.13.0
numpy >= 1.24.0
scikit-fuzzy >= 0.4.2
pandas >= 2.0.0
openpyxl >= 3.1.0


### Network

- Internet connection mandatory for online map tiles
- Minimum speed 1 Mbps, recommended 5 Mbps

---

## 🧪 Testing Criteria

- Loads data files successfully
- Displays all barangays on the map
- Calculates evacuation path on selection
- Highlights optimal route in red
- Displays distance, travel time, and cost metrics properly

---

## 🚢 Deployment

### Streamlit Cloud

- Push code to GitHub repository.
- Connect repository at [share.streamlit.io](https://share.streamlit.io).
- Deploy with a single click.

### Docker

FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]


Build and run:

docker build -t SAFE route .
docker run -p 8501:8501 SAFE route


---

## 🤝 Contributing

- Fork the repo.
- Create feature branch.
- Commit and push changes.
- Open pull request.

Follow PEP 8, document well, and test changes.

---

## 📄 License

MIT License; see [LICENSE](LICENSE).

---

## 👥 Authors

- Your Name — [GitHub Profile](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Municipality of Leon, Iloilo
- Esri Satellite Imagery
- scikit-fuzzy Library
- Streamlit Framework

---

## 📞 Contact

- Email: your.email@example.com
- GitHub Issues: https://github.com/yourusername/leon-evacuation-system/issues

---

## 🗺️ Roadmap

- Real-time traffic integration
- Multiple evacuation centers
- Mobile app support
- Historical evacuation data
- Multi-language support (Filipino, English)
- Weather data integration
- SMS and Email alert features

---

**Made with ❤️ for the safety of Leon, Iloilo**
