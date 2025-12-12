<div align="center">

![banner](IMG/RETAIL.png)

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/YOUR_COLAB_LINK_HERE)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)
![Google Colab](https://img.shields.io/badge/Google%20Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**A powerful web-based analytics platform for retail transaction analysis using Apache Spark and real-time visualizations**

![Dashboard Preview](IMG/dashboard.png)

</div>

---

<div align="center">

## Analytics Capabilities

| Feature | Description |
|---------|-------------|
| **Sales Trends** | Time-series analysis with daily revenue tracking |
| **Top Products** | Identify best-selling items by revenue |
| **Geographic Analysis** | Sales distribution across countries |
| **Basket Analysis** | Discover frequently bought together items |
| **KPI Metrics** | Real-time revenue, orders, customers, items |


## Tech Stack

Backend
<table>
<tr>
<td align="center" width="96">
<img src="https://upload.wikimedia.org/wikipedia/commons/f/f3/Apache_Spark_logo.svg" width="48" height="48" alt="Spark" />
<br><b>PySpark</b>
<br>
</td>
<td align="center" width="96">
<img src="https://www.vectorlogo.zone/logos/pocoo_flask/pocoo_flask-icon.svg" width="48" height="48" alt="Flask" />
<br><b>Flask</b>
<br>
</td>
<td align="center" width="96">
<img src="https://spark.apache.org/images/spark-logo-trademark.png" width="65" height="48" alt="FP-Growth" style="object-fit: contain;" />
<br><b>FP-Growth</b>
<br>
</td>
<td align="center" width="96">
<img src="https://avatars.githubusercontent.com/u/3862302?s=200&v=4" width="48" height="48" alt="Ngrok" />
<br><b>Ngrok</b>
<br>
</td>
</tr>
</table>
Frontend
<table>
<tr>
<td align="center" width="96">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" width="48" height="48" alt="HTML5" />
<br><b>HTML5</b>
<br>
</td>
<td align="center" width="96">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" width="48" height="48" alt="CSS3" />
<br><b>CSS3</b>
<br>
</td>
<td align="center" width="96">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" width="48" height="48" alt="JavaScript" />
<br><b>JavaScript</b>
<br>
</td>
<td align="center" width="96">
<img src="https://www.chartjs.org/img/chartjs-logo.svg" width="48" height="48" alt="Chart.js" />
<br><b>Chart.js</b>
<br>
</td>
<td align="center" width="96">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" width="48" height="48" alt="Glassmorphism" />
<br><b>Glassmorphism</b>
<br>
</td>
</tr>
</table>

</div>

<div align="center">

## Dataset

**UCI Online Retail II** — 540K+ transactions from a UK-based online retailer

[![Dataset](https://img.shields.io/badge/UCI-Dataset-blue?style=flat-square)](https://archive.ics.uci.edu/dataset/502/online+retail+ii)

</div>

---

## Quick Start

**1. Start the Backend (Google Colab)**
```bash
# Upload retail_analysis_spark.ipynb to Google Colab
# Run all cells
# Copy the ngrok URL (e.g., http://xxxx.ngrok-free.app)
```

**2. Start the Frontend (Local)**
```bash
cd "a:\My project\final"
python app.py
```

**3. Access Dashboard**
```
Open: http://127.0.0.1:3000
Paste your ngrok URL and click "Connect"
Upload your CSV dataset
```

**Basket Analysis Parameters:**
- `Min Support`: Minimum frequency threshold (default: 0.01)
- `Min Confidence`: Minimum rule confidence (default: 0.1)

**Recommended for large datasets:** Increase min_support to 0.05+ to reduce memory usage.

<div align="center">

---
   
## Screenshots


### Market Basket Analysis
![Market Basket](IMG/basket.png)

### Sales Trends
![Sales Trends](IMG/sales.PNG)

---

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Local Browser  │ ◄─────► │  Flask Frontend  │
│   (Dashboard)   │         │   (Port 3000)    │
└─────────────────┘         └──────────────────┘
                                     │
                                     │ HTTP
                                     ▼
                            ┌──────────────────┐
                            │  Ngrok Tunnel    │
                            └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Google Colab    │
                            │  ┌────────────┐  │
                            │  │   Spark    │  │
                            │  │   Engine   │  │
                            │  └────────────┘  │
                            │  Flask API (5000)│
                            └──────────────────┘
```


</div>

<!---<div align="center">
[![Star History Chart](https://api.star-history.com/svg?repos=ARUNAGIRINATHAN-K/Retail-Transaction-Analytics&type=Date)](https://star-history.com/#ARUNAGIRINATHAN-K/Retail-Transaction-Analytics&Date)
</div>
--->

<br>

---

<div align="center">

⭐ If this project helped you, please consider giving it a star!

**Made by ARUNAGIRINATHAN K**

**Built with ❤️ using PySpark & Colab**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ARUNAGIRINATHAN-K)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/arunagirinathan-k/)

</div>
