# ✈️ United Airlines Route Profitability Analysis

![Fleet Analysis Dashboard](dashboards/fleet_analysis_dashboard.png)
> *An interactive diagnostic tool for analyzing network efficiency, fleet performance, and unit economics.*

---

## 📖 Project Overview

This project was designed to solve a critical business problem for a mid-sized airline: **identifying which specific routes and aircraft are "bleeding cash" (Negative Operating Contribution).** By visualizing **Unit Economics (RASM vs. CASM)** and **Operating Contribution**, this dashboard moves beyond simple "Revenue" metrics to reveal true profitability. It serves as a "Hub-and-Spoke" diagnostic tool, allowing executives to drill down from a global network view to individual flight performance.

### 🎯 Key Business Questions Answered

- **Network Health:** Which hubs are driving profit, and which are dragging down margins?
- **Route Efficiency:** Which specific routes (e.g., ORD → MIA) are operating at a loss?
- **Fleet Optimization:** Is a route failing due to low demand, or because the wrong aircraft type (e.g., A320 vs B737) is being utilized?
- **Cost Analysis:** Identifying outliers where Operational Costs exceed Revenue per Available Seat Mile (RASM).

---

## 📊 Data Pipeline

### Data Sources

This analysis uses official U.S. Department of Transportation (DoT) Bureau of Transportation Statistics (BTS) datasets:

| Dataset | Description | Purpose |
|---------|-------------|---------|
| **T100 Domestic Segment** | Flight-level operational data (passengers, seats, departures, distance) | Traffic volume & capacity metrics |
| **DB1B Market** | 10% sample of airline ticket data (fares, itineraries) | Pricing & revenue analysis |
| **Form 41 Schedule P-5.2** | Aircraft operating cost data | Hourly operational costs by aircraft type |

### Pipeline Workflow

```mermaid
flowchart LR
    A[Raw BTS Data<br/>T100 + DB1B + Form41] --> B[Python Data Cleaning<br/>clean_data.py]
    B --> C[Filtered UA Data<br/>CSV Files]
    C --> D[SQL Processing<br/>clean_and_merge.sql]
    D --> E[Merged Financial Data<br/>Excel Workbook]
    E --> F[Tableau Visualization<br/>Interactive Dashboards]
```

### Python Scripts

| Script | Purpose |
|--------|---------|
| [`inspect_data.py`](scripts/inspect_data.py) | Initial data exploration and column inspection |
| [`clean_data.py`](scripts/clean_data.py) | Filters for United Airlines (UA), standardizes column names, handles data types |
| [`merge_db1b.py`](scripts/merge_db1b.py) | Merges quarterly DB1B files into a single annual dataset |
| [`process_airline_data.py`](scripts/process_airline_data.py) | End-to-end data processing pipeline |

### SQL Processing

The [`clean and merge.sql`](sql/clean%20and%20merge.sql) script performs:

1. **Data Cleaning:** Removes ferry/maintenance flights (< 20 passengers)
2. **Traffic Aggregation:** Groups by Origin, Destination, and Aircraft Type
3. **Fare Analysis:** Categorizes fares into tiers (Award, Ultra-Low, Standard)
4. **Price Calculation:** Computes weighted average fares per route
5. **Cost Integration:** Joins aircraft hourly operating costs from Form 41
6. **Final Merge:** Creates unified route financial dataset

---

## 📈 Key Metrics & Calculations

### Financial Performance

| Metric | Formula | Description |
|--------|---------|-------------|
| **Total Revenue** | `Avg_Fare × Annual_Pax_Volume` | Gross income from ticket sales |
| **Total Ops Cost** | `Hourly_Cost × Total_Flight_Time + Landing_Costs` | Flight operations + station costs |
| **Op Contribution** | `Total Revenue - Total Ops Cost` | Net Operating Profit |

### Supply & Demand (Volume)

| Metric | Formula | Description |
|--------|---------|-------------|
| **ASM** (Available Seat Miles) | `Annual_Seat_Capacity × Distance_Miles` | Total capacity generated |
| **RPM** (Revenue Passenger Miles) | `Annual_Pax_Volume × Distance_Miles` | Total traffic volume |

### Unit Economics (Efficiency KPIs)

| Metric | Formula | Description |
|--------|---------|-------------|
| **RASM** (Unit Revenue) | `Total Revenue / ASM` | Revenue per Available Seat Mile |
| **CASM** (Unit Cost) | `Total Ops Cost / ASM` | Cost per Available Seat Mile |
| **Load Factor** | `RPM / ASM` | Percentage of seats filled |
| **Yield** | `Total Revenue / RPM` | Average fare paid per mile per passenger |
| **Operating Margin** | `(RASM - CASM) / RASM × 100` | Profitability percentage |

---

## 🛠️ Technical Implementation

Built in **Tableau**, utilizing advanced data modeling and visualization techniques:

### 1. Geospatial & Network Analysis

- **Dual-Axis Map Layers:** Created a custom map separating **Hubs (Origin)** and **Spokes (Destination)** to solve data overlap issues and allow for clear "Hub-to-Spoke" visualization.
- **Spatial Drill-Downs:** Implemented logic to visualize network connections without cluttering the UI.

### 2. Advanced Logic & Calculations

- **Context Filters:** Applied "Add to Context" logic to fix Order of Operations errors, ensuring "Top 10 / Bottom 10" rankings calculate dynamically *after* a specific Hub is selected.
- **Set Actions:** Utilized Tableau Sets for dynamic cohort analysis that adapts to user selection.
- **String Manipulation:** Created custom "Route Keys" (`Origin + " to " + Dest`) to bridge data granularity gaps between different datasets.

### 3. Dashboard Interactivity (The "Diagnostic Flow")

- **Cross-Filtering Actions:** Clicking a Hub filters the entire dashboard (Scatter Plots, Fleet Analysis, Rankings).
- **Highlight Actions:** Configured multi-dimensional highlighting—selecting a route on the scatter plot instantly highlights the specific aircraft responsible in the Fleet Matrix.

---

## 📸 Dashboard Screenshots

### Fleet Analysis Dashboard
![Fleet Analysis](dashboards/fleet_analysis_dashboard.png)

Key visualizations:
- **Network Map:** Hub-and-spoke visualization with size indicating revenue
- **Efficiency by Distance:** Operating margin vs. distance scatter plot
- **Operating Profit by Aircraft:** Ranked bar chart showing aircraft profitability
- **Fleet Utilization:** Total flight time by aircraft type
- **Unit Revenue/Cost by Aircraft:** RASM and CASM comparison charts

### Route Profitability Dashboard
![Route Profitability](dashboards/route_profitability_dashboard.png)

Key visualizations:
- **Economics Scatter (by Aircraft):** RASM vs. CASM by aircraft type
- **Economics Scatter (by Origin):** RASM vs. CASM by hub
- **Top 10 / Worst 10 Routes:** Ranked by Operating Contribution
- **Operating Profit by Route:** Detailed route-level profitability

---

## 🚀 How to Use the Dashboard

1. **Select a Hub:** Click on a large circle (e.g., Chicago - ORD) on the map.
2. **Identify the "Bleeders":** Look at the **"Worst 10 Routes"** chart to see the biggest money-losers.
3. **Diagnose the Cause:** Click a red dot on the **Hub Economics Scatter Plot**.
4. **Pinpoint the Aircraft:** Watch the **Fleet Matrix** highlight to see if a specific aircraft type is underperforming on that route.

---

## 📁 Repository Structure

```
├── README.md                    # This file
├── scripts/                     # Python data processing scripts
│   ├── clean_data.py           # Main data cleaning pipeline
│   ├── merge_db1b.py           # DB1B quarterly merger
│   ├── process_airline_data.py # End-to-end processing
│   └── inspect_data.py         # Data exploration utility
├── sql/                         # SQL queries
│   └── clean and merge.sql     # MySQL data transformation
├── dashboards/                  # Dashboard screenshots
│   ├── fleet_analysis_dashboard.png
│   └── route_profitability_dashboard.png
├── data/                        # Sample data (not included)
│   └── .gitkeep
└── docs/                        # Additional documentation
    └── .gitkeep
```

---

## ⚙️ Setup & Requirements

### Python Dependencies

```bash
pip install pandas
```

### Database Requirements

- MySQL 8.0+ (or compatible)
- Tableau Desktop (for dashboard development)
- Tableau Public (for sharing)

### Data Requirements

Download the following datasets from [BTS TranStats](https://www.transtats.bts.gov/):

1. **T-100 Domestic Segment (US Carriers Only)** - 2024
2. **DB1B Market Survey** - 2024 Q1-Q4
3. **Form 41 Schedule P-5.2** - Aircraft Operating Expenses

---

## 🔗 Links

- **Tableau Public Dashboard:** [View Interactive Dashboard](#) *(Add your Tableau Public link)*
- **BTS TranStats:** [https://www.transtats.bts.gov/](https://www.transtats.bts.gov/)

---

## 👤 Author

**Hrishikesh Sajeev**

- [LinkedIn](#) *(Add your LinkedIn)*
- [Portfolio](#) *(Add your portfolio)*

---

## 📄 License

This project is for educational and portfolio purposes. Data sourced from the U.S. Department of Transportation Bureau of Transportation Statistics.

---

*Created with Python, MySQL, and Tableau Desktop | Data Source: U.S. BTS TranStats*
