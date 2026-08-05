"""
FinSight AI - Configuration File
Contains all settings, constants, and project configuration
"""

import re
from pathlib import Path

# ==================== PROJECT INFO ====================
PROJECT_NAME = "FinSight AI"
PROJECT_SUBTITLE = "Intelligent Stock Market Prediction & Investment Assistant"
VERSION = "1.0.0"
DEVELOPER = ""
TEAM_MEMBERS = ["Priya Yadav", "Diya Verma", "Trisha Sharma", "Ojhal Shekhawat"]
COLLEGE = "Rajasthan College of Engineering for Women"
COURSE = "B.Tech Computer Science Engineering"
PROJECT_TYPE = "Project"

# ==================== STREAMLIT CONFIG ====================
STREAMLIT_CONFIG = {
    "page_title": PROJECT_NAME,
    "page_icon": "📈",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# When deploying on Streamlit Cloud set this environment variable to "1" (or set STREAMLIT_CLOUD_MODE=True)
import os
STREAMLIT_CLOUD_MODE = os.environ.get("STREAMLIT_CLOUD", "0") == "1"

# ==================== UI THEME & COLORS ====================
THEME = {
    "primary": "#1d4ed8",
    "secondary": "#64748b",
    "success": "#059669",
    "danger": "#dc2626",
    "warning": "#d97706",
    "info": "#0284c7",
    "light": "#f8fafc",
    "dark": "#0f172a",
    "background": "#f8fafc",
    "sidebar": "#ffffff",
}

CHART_COLORS = {
    "bullish": "#00cc96",  # Green
    "bearish": "#ef553b",  # Red
    "neutral": "#ab63fa",  # Purple
}

# ==================== TECHNICAL ANALYSIS INDICATORS ====================
MA_PERIODS = [10, 20]  # Moving Average periods
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2

# ==================== MODEL PARAMETERS ====================
MODEL_CONFIG = {
    "model_type": "ExtraTrees",
    "n_estimators": 150,
    "max_depth": 25,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "random_state": 42,
    "n_jobs": -1,
    "test_size": 0.15,
    "train_lookback": 250,  # Trading days (approx 1 year)
    "target_type": "return",  # Predict next-day return rather than raw price
}

# ==================== FEATURES FOR ML MODEL ====================
FEATURE_COLUMNS = [
    "MA10", "MA20", "EMA10", "EMA20", "EMA50",
    "MA_Ratio", "MA_Diff", "EMA_Ratio",
    "RSI", "MACD", "MACD_Signal", "MACD_Hist",
    "BB_High", "BB_Low", "BB_Middle", "BB_PctB", "BB_Width",
    "Daily_Return", "Return_5D", "Return_10D", "Momentum_10",
    "ATR", "Volume_Change", "Close_Open_Ratio", "DayOfWeek",
    "Volatility"
]

# ==================== PREDICTION THRESHOLDS ====================
THRESHOLD_OPTIONS = {
    "0.25%": 0.0025,
    "0.5%": 0.005,
    "0.75%": 0.0075,
    "1%": 0.01,
    "1.25%": 0.0125,
    "1.5%": 0.015,
    "2%": 0.02,
    "2.5%": 0.025,
    "3%": 0.03,
    "4%": 0.04,
    "5%": 0.05,
    "7.5%": 0.075,
    "10%": 0.10,
}

DEFAULT_THRESHOLD = 0.02  # 2% default


def normalize_company_name(value):
    """Normalize company names for reliable blacklist matching."""
    return re.sub(r"[^a-z0-9]+", "", (value or "").strip().lower())


BLOCKED_COMPANY_ALIASES = {
    "Adani Transmission",
    "Adani Wilmar",
    "Alstom India",
    "Cognizant Technology",
    "Contech Solutions",
    "Contech Solution",
    "Essence Electronics",
    "FSN E-Commerce Ventures",
    "FSN E Commerce Ventures",
    "FNS E-Commerce Ventures",
    "GSKPI",
    "GTN Textiles",
    "Gera Advisor",
    "Gal Industries",
    "Hindustan Motors",
    "Hindustan Industries",
    "Hindusthan Industries",
    "Housing Development Finance",
    "Hubballi Auto",
    "Indian Metals",
    "Intel India",
    "Interglobe Finance",
    "Ion Exchange",
    "IPL Plastics",
    "IPL Plastic",
    "Iqvia Holdings",
    "Istara Construction",
    "Island Petrochemicals",
    "Israel Chemicals",
    "Isteel Pvt",
    "Isteel Put",
    "Jio Financial",
    "RIL New Energy",
    "Zomato Limited",
}

BLOCKED_COMPANY_NAMES = {normalize_company_name(name) for name in BLOCKED_COMPANY_ALIASES}


def is_blocked_company_name(name):
    return normalize_company_name(name) in BLOCKED_COMPANY_NAMES


def filter_blocked_companies(company_map):
    if not isinstance(company_map, dict):
        return company_map
    return {name: info for name, info in company_map.items() if not is_blocked_company_name(name)}


# ==================== INDIAN COMPANIES DATABASE ====================
# Contains 200+ Indian companies from NSE and BSE

ALL_INDIAN_COMPANIES = {
    # NIFTY 50 (Tier 1)
    "Reliance Industries Limited": {"NSE": "RELIANCE.NS", "BSE": "500325.BO", "sector": "Energy"},
    "Tata Consultancy Services": {"NSE": "TCS.NS", "BSE": "532540.BO", "sector": "IT"},
    "Infosys Limited": {"NSE": "INFY.NS", "BSE": "500209.BO", "sector": "IT"},
    "Housing Development Finance": {"NSE": "HDFC.NS", "BSE": "500010.BO", "sector": "Finance"},
    "ICICI Bank Limited": {"NSE": "ICICIBANK.NS", "BSE": "532174.BO", "sector": "Banking"},
    "State Bank of India": {"NSE": "SBIN.NS", "BSE": "500112.BO", "sector": "Banking"},
    "Hindustan Unilever": {"NSE": "HINDUNILVR.NS", "BSE": "500696.BO", "sector": "FMCG"},
    "Larsen & Toubro": {"NSE": "LT.NS", "BSE": "500510.BO", "sector": "Engineering"},
    "Bajaj Auto Limited": {"NSE": "BAJAJATO.NS", "BSE": "532976.BO", "sector": "Automobile"},
    "Maruti Suzuki India": {"NSE": "MARUTI.NS", "BSE": "532500.BO", "sector": "Automobile"},
    "Asian Paints India": {"NSE": "ASIANPAINT.NS", "BSE": "500820.BO", "sector": "Paint"},
    "Axis Bank Limited": {"NSE": "AXISBANK.NS", "BSE": "532215.BO", "sector": "Banking"},
    "HDFC Bank Limited": {"NSE": "HDFCBANK.NS", "BSE": "500180.BO", "sector": "Banking"},
    "HDFC Life Insurance": {"NSE": "HDFCLIFE.NS", "BSE": "540777.BO", "sector": "Insurance"},
    "Bharti Airtel Limited": {"NSE": "BHARTIARTL.NS", "BSE": "532454.BO", "sector": "Telecom"},
    "ITC Limited": {"NSE": "ITC.NS", "BSE": "500010.BO", "sector": "Tobacco"},
    "Nestlé India Limited": {"NSE": "NESTLEIND.NS", "BSE": "500900.BO", "sector": "FMCG"},
    "Dr. Reddy's Laboratories": {"NSE": "DRREDDY.NS", "BSE": "500087.BO", "sector": "Pharma"},
    "Lupin Limited": {"NSE": "LUPIN.NS", "BSE": "500257.BO", "sector": "Pharma"},
    "Sun Pharmaceutical": {"NSE": "SUNPHARMA.NS", "BSE": "524715.BO", "sector": "Pharma"},
    "Cipla Limited": {"NSE": "CIPLA.NS", "BSE": "500087.BO", "sector": "Pharma"},
    "JSW Steel Limited": {"NSE": "JSWSTEEL.NS", "BSE": "532171.BO", "sector": "Steel"},
    "Tata Motors Limited": {"NSE": "TATAMOTORS.NS", "BSE": "500570.BO", "sector": "Automobile"},
    "Tata Steel Limited": {"NSE": "TATASTEEL.NS", "BSE": "500470.BO", "sector": "Steel"},
    "Tata Consumer Products": {"NSE": "TATACONSUM.NS", "BSE": "500800.BO", "sector": "FMCG"},
    "Titan Company Limited": {"NSE": "TITAN.NS", "BSE": "999999999.BO", "sector": "Consumer Goods"},
    "Wipro Limited": {"NSE": "WIPRO.NS", "BSE": "532580.BO", "sector": "IT"},
    "Tech Mahindra": {"NSE": "TECHM.NS", "BSE": "532755.BO", "sector": "IT"},
    "Cognizant Technology": {"NSE": "COGNIZANT.NS", "BSE": "999999999.BO", "sector": "IT"},
    "HCL Technologies": {"NSE": "HCLTECH.NS", "BSE": "532723.BO", "sector": "IT"},
    "Ultratech Cement": {"NSE": "ULTRACEMCO.NS", "BSE": "500696.BO", "sector": "Cement"},
    "Ambuja Cements": {"NSE": "AMBUJACEM.NS", "BSE": "500409.BO", "sector": "Cement"},
    "Shree Cement": {"NSE": "SHREECEM.NS", "BSE": "532708.BO", "sector": "Cement"},
    "ACC Limited": {"NSE": "ACC.NS", "BSE": "500006.BO", "sector": "Cement"},
    "Bajaj Finance": {"NSE": "BAJAJFINSV.NS", "BSE": "532978.BO", "sector": "Finance"},
    "Kotak Mahindra Bank": {"NSE": "KOTAKBANK.NS", "BSE": "532464.BO", "sector": "Banking"},
    "IndusInd Bank": {"NSE": "INDUSINDBK.NS", "BSE": "532187.BO", "sector": "Banking"},
    "Oil and Natural Gas": {"NSE": "ONGC.NS", "BSE": "500312.BO", "sector": "Energy"},
    "Indian Oil Corporation": {"NSE": "IOC.NS", "BSE": "530965.BO", "sector": "Energy"},
    "Bharat Petroleum": {"NSE": "BPCL.NS", "BSE": "500103.BO", "sector": "Energy"},
    "Hero MotoCorp": {"NSE": "HEROMOTOCO.NS", "BSE": "500182.BO", "sector": "Automobile"},
    "Mahindra & Mahindra": {"NSE": "MM.NS", "BSE": "500581.BO", "sector": "Automobile"},
    "Bharati V-Art": {"NSE": "BHARTIARTL.NS", "BSE": "532454.BO", "sector": "Telecom"},
    "Vodafone Idea": {"NSE": "VODAFONE.NS", "BSE": "532536.BO", "sector": "Telecom"},
    "Jio Financial": {"NSE": "JIOFINANCE.NS", "BSE": "999999999.BO", "sector": "Finance"},
    "Coal India Limited": {"NSE": "COALINDIA.NS", "BSE": "533278.BO", "sector": "Energy"},
    "Power Grid Corporation": {"NSE": "POWERGRID.NS", "BSE": "532898.BO", "sector": "Energy"},
    "Paytm Limited": {"NSE": "PAYTM.NS", "BSE": "999999999.BO", "sector": "Technology"},
    "NTPC Limited": {"NSE": "NTPC.NS", "BSE": "506239.BO", "sector": "Energy"},
    "Gail India Limited": {"NSE": "GAIL.NS", "BSE": "532155.BO", "sector": "Energy"},
    "RIL New Energy": {"NSE": "RILNRGY.NS", "BSE": "999999999.BO", "sector": "Energy"},
    "Grasim Industries": {"NSE": "GRASIM.NS", "BSE": "500182.BO", "sector": "Cement"},
    
    # Midcap & Smallcap Companies (Extended List)
    "3M India Limited": {"NSE": "3MINDIA.NS", "BSE": "500002.BO", "sector": "Diversified"},
    "Adani Enterprises": {"NSE": "ADANIENT.NS", "BSE": "532185.BO", "sector": "Infrastructure"},
    "Adani Ports": {"NSE": "ADANIPORTS.NS", "BSE": "532205.BO", "sector": "Ports"},
    "Adani Power": {"NSE": "ADANIPOWER.NS", "BSE": "532217.BO", "sector": "Power"},
    "Adani Total Gas": {"NSE": "ADANIGAS.NS", "BSE": "532220.BO", "sector": "Gas"},
    "Adani Green Energy": {"NSE": "ADANIGREEN.NS", "BSE": "999999999.BO", "sector": "Energy"},
    "Apollo Hospitals": {"NSE": "APOLLOHOSP.NS", "BSE": "532537.BO", "sector": "Healthcare"},
    "Ashok Leyland": {"NSE": "ASHOKLEY.NS", "BSE": "500009.BO", "sector": "Automobile"},
    "Aurobindo Pharma": {"NSE": "AUOPHARMA.NS", "BSE": "532348.BO", "sector": "Pharma"},
    "Avalon Technologies": {"NSE": "AVALONTECH.NS", "BSE": "532724.BO", "sector": "IT"},
    "Axis Bank": {"NSE": "AXISBANK.NS", "BSE": "532215.BO", "sector": "Banking"},
    "Bajaj Finserv": {"NSE": "BAJAJFINSV.NS", "BSE": "532978.BO", "sector": "Finance"},
    "Bajaj Holdings": {"NSE": "BAJAJTINSV.NS", "BSE": "532977.BO", "sector": "Finance"},
    "Bank of Baroda": {"NSE": "BANKBARODA.NS", "BSE": "532134.BO", "sector": "Banking"},
    "Bank of India": {"NSE": "BANKINDIA.NS", "BSE": "532149.BO", "sector": "Banking"},
    "Berger Paints": {"NSE": "BERGEPAINT.NS", "BSE": "500493.BO", "sector": "Paint"},
    "BGR Energy": {"NSE": "BGRENERGY.NS", "BSE": "532762.BO", "sector": "Energy"},
    "Biocon Limited": {"NSE": "BIOCON.NS", "BSE": "532522.BO", "sector": "Pharma"},
    "Blue Dart Express": {"NSE": "BLUEDART.NS", "BSE": "500056.BO", "sector": "Logistics"},
    "Bosch Limited": {"NSE": "BOSCHLTD.NS", "BSE": "500081.BO", "sector": "Engineering"},
    "Britannia Industries": {"NSE": "BRITANNIA.NS", "BSE": "532099.BO", "sector": "FMCG"},
    "Cadila Healthcare": {"NSE": "CADILAHC.NS", "BSE": "532346.BO", "sector": "Pharma"},
    "Canara Bank": {"NSE": "CANARABANK.NS", "BSE": "532482.BO", "sector": "Banking"},
    "Ceat Limited": {"NSE": "CEAT.NS", "BSE": "500115.BO", "sector": "Tyres"},
    "Colgate Palmolive": {"NSE": "COLPAL.NS", "BSE": "500097.BO", "sector": "FMCG"},
    "Contech Solutions": {"NSE": "CONTECH.NS", "BSE": "999999999.BO", "sector": "Engineering"},
    "Container Corporation": {"NSE": "CONCOR.NS", "BSE": "500085.BO", "sector": "Logistics"},
    "Dabur India": {"NSE": "DABUR.NS", "BSE": "500103.BO", "sector": "FMCG"},
    "DCM Shriram": {"NSE": "DCMSHRIRAM.NS", "BSE": "500114.BO", "sector": "Chemicals"},
    "Deepak Fertilizers": {"NSE": "DEEPAKFERT.NS", "BSE": "532521.BO", "sector": "Fertilizers"},
    "Divi's Laboratories": {"NSE": "DIVISLAB.NS", "BSE": "532381.BO", "sector": "Pharma"},
    "Dixon Technologies": {"NSE": "DIXON.NS", "BSE": "532890.BO", "sector": "Electronics"},
    "Dow Chemical": {"NSE": "DOWCHEM.NS", "BSE": "532127.BO", "sector": "Chemicals"},
    "EIL Limited": {"NSE": "EIL.NS", "BSE": "532203.BO", "sector": "Engineering"},
    "Essence Electronics": {"NSE": "ESSENCETECH.NS", "BSE": "999999999.BO", "sector": "Electronics"},
    "Escorts Limited": {"NSE": "ESCORTS.NS", "BSE": "500182.BO", "sector": "Automobile"},
    "Exicom Tele Systems": {"NSE": "EXICOM.NS", "BSE": "999999999.BO", "sector": "Telecom"},
    "Federal Bank": {"NSE": "FEDERALBNK.NS", "BSE": "532174.BO", "sector": "Banking"},
    "Fertilizers Corporation": {"NSE": "FERTINDIA.NS", "BSE": "532131.BO", "sector": "Fertilizers"},
    "Finolex Cables": {"NSE": "FINOLEX.NS", "BSE": "532382.BO", "sector": "Cables"},
    "Genesys International": {"NSE": "GENESYS.NS", "BSE": "532849.BO", "sector": "IT"},
    "Gera Advisor": {"NSE": "GERA.NS", "BSE": "999999999.BO", "sector": "Real Estate"},
    "Gillette India": {"NSE": "GILLETTE.NS", "BSE": "500170.BO", "sector": "FMCG"},
    "Glaxo Smithkline": {"NSE": "GLAXO.NS", "BSE": "532217.BO", "sector": "Pharma"},
    "GMR Infrastructure": {"NSE": "GMRINFRA.NS", "BSE": "532532.BO", "sector": "Infrastructure"},
    "Go Digit Insurance": {"NSE": "GODIGIT.NS", "BSE": "999999999.BO", "sector": "Insurance"},
    "Godrej & Boyce": {"NSE": "GODREJBOYE.NS", "BSE": "500132.BO", "sector": "Diversified"},
    "Godrej Industries": {"NSE": "GODREJIND.NS", "BSE": "500124.BO", "sector": "Diversified"},
    "Goldtech Pharmaceuticals": {"NSE": "GOLDTECH.NS", "BSE": "999999999.BO", "sector": "Pharma"},
    "Graphite India": {"NSE": "GRAPHITE.NS", "BSE": "500182.BO", "sector": "Mining"},
    "Greaves Leasing": {"NSE": "GREAVESCOT.NS", "BSE": "500160.BO", "sector": "Leasing"},
    "Greenply Industries": {"NSE": "GREENPLY.NS", "BSE": "532487.BO", "sector": "Plywood"},
    "Grindwell Norton": {"NSE": "GRINDWELL.NS", "BSE": "532189.BO", "sector": "Abrasives"},
    "Grl Industries": {"NSE": "GRLINDUSTRI.NS", "BSE": "999999999.BO", "sector": "Engineering"},
    "GSKPI": {"NSE": "GSKPI.NS", "BSE": "999999999.BO", "sector": "Pharma"},
    "GTN Textiles": {"NSE": "GTNTEXTIL.NS", "BSE": "999999999.BO", "sector": "Textiles"},
    "Gujrat Fluorochemicals": {"NSE": "GUJFLUORO.NS", "BSE": "532532.BO", "sector": "Chemicals"},
    "Gujarat Gas": {"NSE": "GUJARATGAS.NS", "BSE": "532218.BO", "sector": "Gas"},
    "Hindustan Aeronautics": {"NSE": "HAL.NS", "BSE": "500009.BO", "sector": "Aerospace"},
    "Hindustan Copper": {"NSE": "HINDALCO.NS", "BSE": "500696.BO", "sector": "Mining"},
    "Hindustan Motors": {"NSE": "HINDMOTOR.NS", "BSE": "500182.BO", "sector": "Automobile"},
    "Hindustan Petroleum": {"NSE": "HINDPETRO.NS", "BSE": "500104.BO", "sector": "Energy"},
    "Hindustan Shipyard": {"NSE": "HINDSHIP.NS", "BSE": "532574.BO", "sector": "Shipbuilding"},
    "Hindusthan Industries": {"NSE": "HINDSTEEL.NS", "BSE": "500182.BO", "sector": "Steel"},
    "Hindalco Industries": {"NSE": "HINDALCO.NS", "BSE": "500696.BO", "sector": "Mining"},
    "Hi-Tech Pharma": {"NSE": "HITECH.NS", "BSE": "999999999.BO", "sector": "Pharma"},
    "Home First Finance": {"NSE": "HOMEFIRST.NS", "BSE": "532913.BO", "sector": "Finance"},
    "Housing Development Finance": {"NSE": "HDFC.NS", "BSE": "500010.BO", "sector": "Finance"},
    "HSBC India": {"NSE": "HSBCBANK.NS", "BSE": "500040.BO", "sector": "Banking"},
    "Hubballi Auto": {"NSE": "HUBLI.NS", "BSE": "999999999.BO", "sector": "Automobile"},
    "Hyundai Motor": {"NSE": "HYUNDAI.NS", "BSE": "532942.BO", "sector": "Automobile"},
    "Icici Securities": {"NSE": "ICICISEC.NS", "BSE": "532349.BO", "sector": "Finance"},
    "ICICI Prudential": {"NSE": "ICICIPRULI.NS", "BSE": "532978.BO", "sector": "Insurance"},
    "Ideaforge Technology": {"NSE": "IDEAFORGE.NS", "BSE": "532974.BO", "sector": "Electronics"},
    "Igas Energy": {"NSE": "IGAS.NS", "BSE": "532968.BO", "sector": "Energy"},
    "Indiabulls Real Estate": {"NSE": "IBULREALTY.NS", "BSE": "532161.BO", "sector": "Real Estate"},
    "Indiabulls Housing": {"NSE": "IBULHSGFIN.NS", "BSE": "532523.BO", "sector": "Finance"},
    "Indian Bank": {"NSE": "INDIANBANK.NS", "BSE": "500093.BO", "sector": "Banking"},
    "Indian Hotels": {"NSE": "INDHOTEL.NS", "BSE": "500182.BO", "sector": "Hospitality"},
    "Indian Metals": {"NSE": "INDIANMET.NS", "BSE": "500182.BO", "sector": "Mining"},
    "Indian Oil": {"NSE": "IOC.NS", "BSE": "530965.BO", "sector": "Energy"},
    "Indian Rayon": {"NSE": "INDIANRAYN.NS", "BSE": "502896.BO", "sector": "Textiles"},
    "Indigo Airlines": {"NSE": "INDIGO.NS", "BSE": "532885.BO", "sector": "Aviation"},
    "Indigo Paints": {"NSE": "INDIGOPAINT.NS", "BSE": "532969.BO", "sector": "Paint"},
    "Indraprastha Gas": {"NSE": "IGL.NS", "BSE": "532179.BO", "sector": "Gas"},
    "Indus Towers": {"NSE": "INDUSTOWER.NS", "BSE": "532891.BO", "sector": "Telecom"},
    "Infibeam Avenues": {"NSE": "INFIBEAM.NS", "BSE": "532976.BO", "sector": "E-commerce"},
    "Integrated Infratech": {"NSE": "IITL.NS", "BSE": "999999999.BO", "sector": "Infrastructure"},
    "Intel India": {"NSE": "INTEL.NS", "BSE": "532187.BO", "sector": "Electronics"},
    "Interglobe Finance": {"NSE": "INTERGLOB.NS", "BSE": "532885.BO", "sector": "Finance"},
    "InterGlobe Aviation": {"NSE": "INDIGO.NS", "BSE": "532885.BO", "sector": "Aviation"},
    "Ion Exchange": {"NSE": "ION.NS", "BSE": "500182.BO", "sector": "Equipment"},
    "Ipl Plastics": {"NSE": "IPLPLAS.NS", "BSE": "999999999.BO", "sector": "Plastics"},
    "Iqvia Holdings": {"NSE": "IQVIA.NS", "BSE": "999999999.BO", "sector": "Healthcare"},
    "Isec Plc": {"NSE": "ISEC.NS", "BSE": "532980.BO", "sector": "Finance"},
    "Ishtara Construction": {"NSE": "ISHTARA.NS", "BSE": "999999999.BO", "sector": "Construction"},
    "Island Petrochemicals": {"NSE": "ISLANDPCS.NS", "BSE": "999999999.BO", "sector": "Chemicals"},
    "Israel Chemicals": {"NSE": "ISRCLM.NS", "BSE": "999999999.BO", "sector": "Chemicals"},
    "Isteel Pvt": {"NSE": "ISTEEL.NS", "BSE": "999999999.BO", "sector": "Steel"},
    "SBI Life Insurance": {"NSE": "SBILIFE.NS", "BSE": "999999999.BO", "sector": "Insurance"},
    "Tata Power Company": {"NSE": "TATAPOWER.NS", "BSE": "532179.BO", "sector": "Energy"},
    "JSW Energy": {"NSE": "JSWENERGY.NS", "BSE": "532151.BO", "sector": "Energy"},
    "Adani Transmission": {"NSE": "ADANITRANS.NS", "BSE": "999999999.BO", "sector": "Power"},
    "Zomato Limited": {"NSE": "ZOMATO.NS", "BSE": "999999999.BO", "sector": "E-commerce"},
    "Marico Limited": {"NSE": "MARICO.NS", "BSE": "500183.BO", "sector": "FMCG"},
    "Pidilite Industries": {"NSE": "PIDILITIND.NS", "BSE": "500331.BO", "sector": "Chemicals"},
    "Motherson Sumi Systems": {"NSE": "MOTHERSUMI.NS", "BSE": "517334.BO", "sector": "Auto Components"},
    "Bharat Forge": {"NSE": "BHARATFORG.NS", "BSE": "500493.BO", "sector": "Auto Components"},
    "Avenue Supermarts": {"NSE": "DMART.NS", "BSE": "540005.BO", "sector": "Retail"},
    "LTIMindtree": {"NSE": "LTIM.NS", "BSE": "541700.BO", "sector": "IT"},
    "L&T Technology Services": {"NSE": "LTTS.NS", "BSE": "999999999.BO", "sector": "IT Services"},
    "Godrej Consumer Products": {"NSE": "GODREJCP.NS", "BSE": "533106.BO", "sector": "FMCG"},
    "FSN E-Commerce Ventures": {"NSE": "FSN.NS", "BSE": "999999999.BO", "sector": "E-commerce"},
    "Emami Limited": {"NSE": "EMAMILTD.NS", "BSE": "500271.BO", "sector": "FMCG"},
    "Havells India": {"NSE": "HAVELLS.NS", "BSE": "517354.BO", "sector": "Electronics"},
    "Adani Wilmar": {"NSE": "ADANIWIL.NS", "BSE": "999999999.BO", "sector": "Consumer Goods"},
    "Zee Entertainment Enterprises": {"NSE": "ZEEL.NS", "BSE": "500209.BO", "sector": "Media"},
    "Torrent Pharmaceuticals": {"NSE": "TORNTPHARM.NS", "BSE": "500420.BO", "sector": "Pharma"},
    "Voltas Limited": {"NSE": "VOLTAS.NS", "BSE": "500575.BO", "sector": "Consumer Durables"},
    "Procter & Gamble Hygiene": {"NSE": "PGHH.NS", "BSE": "999999999.BO", "sector": "FMCG"},
    "Glenmark Pharmaceuticals": {"NSE": "GLENMARK.NS", "BSE": "999999999.BO", "sector": "Pharma"},
    "Jindal Steel & Power": {"NSE": "JINDALSTEL.NS", "BSE": "505790.BO", "sector": "Steel"},
    "Zydus Lifesciences": {"NSE": "ZYDUSLIFE.NS", "BSE": "999999999.BO", "sector": "Pharma"},
    "Jubilant FoodWorks": {"NSE": "JUBLFOOD.NS", "BSE": "532581.BO", "sector": "Food"},
    "Tata Communications": {"NSE": "TATACOMM.NS", "BSE": "532812.BO", "sector": "Telecom"},
    "Eicher Motors": {"NSE": "EICHERMOT.NS", "BSE": "505200.BO", "sector": "Automobile"},
    "PVR INOX": {"NSE": "PVR.NS", "BSE": "533228.BO", "sector": "Entertainment"},
    "Tata Elxsi": {"NSE": "TATAELXSI.NS", "BSE": "999999999.BO", "sector": "IT Services"},
    "Kansai Nerolac Paints": {"NSE": "KANSANER.NS", "BSE": "500828.BO", "sector": "Paint"},
    "Muthoot Finance": {"NSE": "MUTHOOTFIN.NS", "BSE": "533398.BO", "sector": "Finance"},
    "LIC India": {"NSE": "LICI.NS", "BSE": "540000.BO", "sector": "Insurance"},
    "Alkem Laboratories": {"NSE": "ALKEM.NS", "BSE": "533573.BO", "sector": "Pharma"},
    "Godrej Properties": {"NSE": "GODREJPROP.NS", "BSE": "533076.BO", "sector": "Real Estate"},
    "HDFC Asset Management": {"NSE": "HDFCAMC.NS", "BSE": "999999999.BO", "sector": "Finance"},
    "UPL Limited": {"NSE": "UPL.NS", "BSE": "512070.BO", "sector": "Agrochemicals"},
    "Apollo Tyres": {"NSE": "APOLLOTYRE.NS", "BSE": "500877.BO", "sector": "Tyres"},
    "SBI Cards and Payment Services": {"NSE": "SBICARD.NS", "BSE": "543543.BO", "sector": "Finance"},
    "Siemens India": {"NSE": "SIEMENS.NS", "BSE": "522224.BO", "sector": "Engineering"},
    "Power Finance Corporation": {"NSE": "PFC.NS", "BSE": "532283.BO", "sector": "Finance"},
    "Steel Authority of India": {"NSE": "SAIL.NS", "BSE": "500227.BO", "sector": "Steel"},
    "Petronet LNG": {"NSE": "PETRONET.NS", "BSE": "532522.BO", "sector": "Energy"},
    "Hindustan Petroleum Corporation": {"NSE": "HINDPETRO.NS", "BSE": "500104.BO", "sector": "Energy"},
    "BEML Limited": {"NSE": "BEML.NS", "BSE": "532813.BO", "sector": "Engineering"},
    "NHPC Limited": {"NSE": "NHPC.NS", "BSE": "533098.BO", "sector": "Energy"},
    "Oil India": {"NSE": "OIL.NS", "BSE": "513411.BO", "sector": "Energy"},
    "Max Financial Services": {"NSE": "MFSL.NS", "BSE": "540540.BO", "sector": "Finance"},
    "TVS Motor Company": {"NSE": "TVSMOTOR.NS", "BSE": "532343.BO", "sector": "Automobile"},
    "Borosil Limited": {"NSE": "BOROLTD.NS", "BSE": "532742.BO", "sector": "Glass"},
}

# Expanded company universe for broader Yahoo Finance coverage
ADDITIONAL_COMPANIES = {
    "Bharat Electronics": {"NSE": "BEL.NS", "BSE": "500049.BO", "sector": "Defense"},
    "Indian Railway Finance Corporation": {"NSE": "IRFC.NS", "BSE": "543257.BO", "sector": "Finance"},
    "Punjab National Bank": {"NSE": "PNB.NS", "BSE": "532461.BO", "sector": "Banking"},
    "IDFC First Bank": {"NSE": "IDFCFIRSTB.NS", "BSE": "539437.BO", "sector": "Banking"},
    "Shriram Finance": {"NSE": "SHRIRAMFIN.NS", "BSE": "511218.BO", "sector": "Finance"},
    "Bandhan Bank": {"NSE": "BANDHANBNK.NS", "BSE": "541153.BO", "sector": "Banking"},
    "AU Small Finance Bank": {"NSE": "AUBANK.NS", "BSE": "540611.BO", "sector": "Banking"},
    "DLF Limited": {"NSE": "DLF.NS", "BSE": "532868.BO", "sector": "Real Estate"},
    "L&T Finance Holdings": {"NSE": "LTFH.NS", "BSE": "533519.BO", "sector": "Finance"},
    "Cholamandalam Investment and Finance": {"NSE": "CHOLAFIN.NS", "BSE": "511243.BO", "sector": "Finance"},
    "Mankind Pharma": {"NSE": "MANKIND.NS", "BSE": "543529.BO", "sector": "Pharma"},
    "Dr. Lal PathLabs": {"NSE": "LALPATHLAB.NS", "BSE": "539551.BO", "sector": "Healthcare"},
    "Syngene International": {"NSE": "SYNGENE.NS", "BSE": "539665.BO", "sector": "Healthcare"},
    "Laurus Labs": {"NSE": "LAURUSLABS.NS", "BSE": "540222.BO", "sector": "Pharma"},
    "Sun TV Network": {"NSE": "SUNTV.NS", "BSE": "532733.BO", "sector": "Media"},
    "Aarti Industries": {"NSE": "AARTIIND.NS", "BSE": "524208.BO", "sector": "Chemicals"},
    "Balkrishna Industries": {"NSE": "BALKRISIND.NS", "BSE": "502355.BO", "sector": "Tyres"},
    "MRF Limited": {"NSE": "MRF.NS", "BSE": "500290.BO", "sector": "Tyres"},
    "SRF Limited": {"NSE": "SRF.NS", "BSE": "503440.BO", "sector": "Chemicals"},
    "Atul Limited": {"NSE": "ATUL.NS", "BSE": "500027.BO", "sector": "Chemicals"},
    "Abbott India": {"NSE": "ABBOTINDIA.NS", "BSE": "500488.BO", "sector": "Healthcare"},
    "Crompton Greaves Consumer": {"NSE": "CROMPTON.NS", "BSE": "500093.BO", "sector": "Consumer Durables"},
    "Gland Pharma": {"NSE": "GLAND.NS", "BSE": "543245.BO", "sector": "Pharma"},
    "The Ramco Cements": {"NSE": "RAMCOCEM.NS", "BSE": "500260.BO", "sector": "Cement"},
    "Kalyan Jewellers": {"NSE": "KALYANKJIL.NS", "BSE": "535149.BO", "sector": "Retail"},
    "Polycab India": {"NSE": "POLYCAB.NS", "BSE": "542652.BO", "sector": "Electrical"},
    "Angel One": {"NSE": "ANGELONE.NS", "BSE": "543235.BO", "sector": "Finance"},
    "Persistent Systems": {"NSE": "PERSISTENT.NS", "BSE": "533179.BO", "sector": "IT"},
    "KPIT Technologies": {"NSE": "KPITTECH.NS", "BSE": "542651.BO", "sector": "IT"},
    "Coforge": {"NSE": "COFORGE.NS", "BSE": "532541.BO", "sector": "IT"},
    "Mphasis": {"NSE": "MPHASIS.NS", "BSE": "526299.BO", "sector": "IT"},
    "AIA Engineering": {"NSE": "AIAENG.NS", "BSE": "532683.BO", "sector": "Engineering"},
    "NCC Limited": {"NSE": "NCC.NS", "BSE": "500294.BO", "sector": "Infrastructure"},
    "Mahanagar Gas": {"NSE": "MGL.NS", "BSE": "539957.BO", "sector": "Gas"},
    "Gujarat State Petronet": {"NSE": "GSPL.NS", "BSE": "532702.BO", "sector": "Energy"},
    "Jindal Stainless": {"NSE": "JSL.NS", "BSE": "533267.BO", "sector": "Steel"},
    "UCO Bank": {"NSE": "UCOBANK.NS", "BSE": "532505.BO", "sector": "Banking"},
    "GMR Airports": {"NSE": "GMRAIRPORTS.NS", "BSE": "532953.BO", "sector": "Infrastructure"},
    "Tata Chemicals": {"NSE": "TATACHEM.NS", "BSE": "500770.BO", "sector": "Chemicals"},
    "Vedanta Limited": {"NSE": "VEDL.NS", "BSE": "500295.BO", "sector": "Mining"},
    "NMDC Limited": {"NSE": "NMDC.NS", "BSE": "526371.BO", "sector": "Mining"},
    "Sundaram Finance": {"NSE": "SUNDARMFIN.NS", "BSE": "590071.BO", "sector": "Finance"},
    "BSE Limited": {"NSE": "BSE.NS", "BSE": "532715.BO", "sector": "Financial Services"},
    "Tata Investment Corporation": {"NSE": "TATAINVEST.NS", "BSE": "501301.BO", "sector": "Finance"},
    "Jio Financial Services": {"NSE": "JIOFIN.NS", "BSE": "543526.BO", "sector": "Finance"},
    "Tata Technologies": {"NSE": "TATATECH.NS", "BSE": "544028.BO", "sector": "IT"},
    "Aster DM Healthcare": {"NSE": "ASTERDM.NS", "BSE": "543254.BO", "sector": "Healthcare"},
    "Fortis Healthcare": {"NSE": "FORTIS.NS", "BSE": "531531.BO", "sector": "Healthcare"},
    "Max Healthcare": {"NSE": "MAXHEALTH.NS", "BSE": "543220.BO", "sector": "Healthcare"},
    "Lemon Tree Hotels": {"NSE": "LEMONTREE.NS", "BSE": "541506.BO", "sector": "Hospitality"},
    "Piramal Enterprises": {"NSE": "PIRAMAL.NS", "BSE": "523000.BO", "sector": "Finance"},
    "Navin Fluorine International": {"NSE": "NAVINFLUOR.NS", "BSE": "532720.BO", "sector": "Chemicals"},
    "Aegis Logistics": {"NSE": "AEGISLOG.NS", "BSE": "500003.BO", "sector": "Logistics"},
    "Bharat Rasayan": {"NSE": "BHARATRAS.NS", "BSE": "524730.BO", "sector": "Chemicals"},
    "Prince Pipes and Fittings": {"NSE": "PRINCEPIPE.NS", "BSE": "543261.BO", "sector": "Plastics"},
    "Poonawalla Fincorp": {"NSE": "POONAWALLA.NS", "BSE": "543335.BO", "sector": "Finance"},
    "Sona BLW Precision Forgings": {"NSE": "SONABLW.NS", "BSE": "543300.BO", "sector": "Auto Components"},
    "Sapphire Foods": {"NSE": "SAPPHIRE.NS", "BSE": "543397.BO", "sector": "Food"},
    "Dixon Technologies": {"NSE": "DIXON.NS", "BSE": "532890.BO", "sector": "Electronics"},
    "Narayana Hrudayalaya": {"NSE": "NH.NS", "BSE": "539551.BO", "sector": "Healthcare"},
    "Jubilant Pharmova": {"NSE": "JUBLPHARMA.NS", "BSE": "530019.BO", "sector": "Pharma"},
    "Bikaji Foods": {"NSE": "BIKAJIFIN.NS", "BSE": "543383.BO", "sector": "Food"},
}

for _name, _info in ADDITIONAL_COMPANIES.items():
    if _name not in ALL_INDIAN_COMPANIES:
        ALL_INDIAN_COMPANIES[_name] = _info

# Additional large-cap and mid-cap Indian companies to broaden coverage further
EXTENDED_COMPANIES = {
    "ABB India Limited": {"NSE": "ABB.NS", "BSE": "500002.BO", "sector": "Industrial"},
    "Airtel Africa": {"NSE": "BHARTIARTL.NS", "BSE": "532454.BO", "sector": "Telecom"},
    "Ajanta Pharma": {"NSE": "AJANTPHARM.NS", "BSE": "532331.BO", "sector": "Pharma"},
    "Allcargo Logistics": {"NSE": "ALLCARGO.NS", "BSE": "532749.BO", "sector": "Logistics"},
    "Alstom India": {"NSE": "ALSTOMT&D.NS", "BSE": "533278.BO", "sector": "Engineering"},
    "Amara Raja Batteries": {"NSE": "AMARAJABAT.NS", "BSE": "500008.BO", "sector": "Automobile"},
    "Andhra Paper": {"NSE": "ANDHAPAP.NS", "BSE": "500012.BO", "sector": "Paper"},
    "Apar Industries": {"NSE": "APARINDS.NS", "BSE": "532259.BO", "sector": "Chemicals"},
    "Arvind Limited": {"NSE": "ARVIND.NS", "BSE": "500043.BO", "sector": "Textiles"},
    "Ashiana Housing": {"NSE": "ASHIANA.NS", "BSE": "500877.BO", "sector": "Real Estate"},
    "Astrazeneca Pharma": {"NSE": "ASTRAZENCA.NS", "BSE": "506820.BO", "sector": "Pharma"},
    "Avenue Supermarts": {"NSE": "DMART.NS", "BSE": "540005.BO", "sector": "Retail"},
    "BASF India": {"NSE": "BASF.NS", "BSE": "500042.BO", "sector": "Chemicals"},
    "BEML Limited": {"NSE": "BEML.NS", "BSE": "532813.BO", "sector": "Engineering"},
    "Bharat Dynamics": {"NSE": "BDL.NS", "BSE": "541076.BO", "sector": "Defense"},
    "Bharat Electronics": {"NSE": "BEL.NS", "BSE": "500049.BO", "sector": "Defense"},
    "Bharat Heavy Electricals": {"NSE": "BHEL.NS", "BSE": "500103.BO", "sector": "Engineering"},
    "Bharat Rasayan": {"NSE": "BHARATRAS.NS", "BSE": "524730.BO", "sector": "Chemicals"},
    "Bikaji Foods": {"NSE": "BIKAJIFIN.NS", "BSE": "543383.BO", "sector": "Food"},
    "Blue Star": {"NSE": "BLUESTARCO.NS", "BSE": "500067.BO", "sector": "Consumer Durables"},
    "Bombay Burmah Trading": {"NSE": "BBTC.NS", "BSE": "501334.BO", "sector": "Plantations"},
    "Can Fin Homes": {"NSE": "CANFINHOME.NS", "BSE": "511196.BO", "sector": "Finance"},
    "Caplin Point Laboratories": {"NSE": "CAPLIPOINT.NS", "BSE": "524164.BO", "sector": "Pharma"},
    "Carborundum Universal": {"NSE": "CARBORUNIV.NS", "BSE": "508814.BO", "sector": "Materials"},
    "Century Textiles": {"NSE": "CENTURYTEX.NS", "BSE": "500040.BO", "sector": "Textiles"},
    "Chambal Fertilizers": {"NSE": "CHAMBLFERT.NS", "BSE": "500300.BO", "sector": "Fertilizers"},
    "Chennai Petrochem": {"NSE": "CHENNPETRO.NS", "BSE": "500730.BO", "sector": "Energy"},
    "Crompton Greaves": {"NSE": "CROMPTON.NS", "BSE": "500093.BO", "sector": "Consumer Durables"},
    "Cummins India": {"NSE": "CUMMINSIND.NS", "BSE": "500480.BO", "sector": "Engineering"},
    "Dalmia Bharat": {"NSE": "DALBHARAT.NS", "BSE": "533256.BO", "sector": "Cement"},
    "Delta Corp": {"NSE": "DELTACORP.NS", "BSE": "532848.BO", "sector": "Gaming"},
    "Dish TV": {"NSE": "DISHTV.NS", "BSE": "532839.BO", "sector": "Media"},
    "DLF Limited": {"NSE": "DLF.NS", "BSE": "532868.BO", "sector": "Real Estate"},
    "Edelweiss Financial": {"NSE": "EDELWEISS.NS", "BSE": "532922.BO", "sector": "Finance"},
    "Elgi Equipments": {"NSE": "ELGIEQUIP.NS", "BSE": "500085.BO", "sector": "Engineering"},
    "Endurance Technologies": {"NSE": "ENDURANCE.NS", "BSE": "543312.BO", "sector": "Auto Components"},
    "Engineers India": {"NSE": "ENGINERSIND.NS", "BSE": "532178.BO", "sector": "Engineering"},
    "Equitas Small Finance Bank": {"NSE": "EQUITASBNK.NS", "BSE": "540556.BO", "sector": "Banking"},
    "Eris Lifesciences": {"NSE": "ERIS.NS", "BSE": "540596.BO", "sector": "Pharma"},
    "Escorts Kubota": {"NSE": "ESCORTS.NS", "BSE": "500182.BO", "sector": "Engineering"},
    "FDC Limited": {"NSE": "FDC.NS", "BSE": "531350.BO", "sector": "Pharma"},
    "Finolex Industries": {"NSE": "FINOLEXIND.NS", "BSE": "500940.BO", "sector": "Cables"},
    "Firstsource Solutions": {"NSE": "FSL.NS", "BSE": "532809.BO", "sector": "IT"},
    "Ganesha Ecosphere": {"NSE": "GANESHHOUC.NS", "BSE": "543237.BO", "sector": "Plastics"},
    "Garden Reach Shipbuilders": {"NSE": "GRSE.NS", "BSE": "542851.BO", "sector": "Defense"},
    "Glenmark Pharma": {"NSE": "GLENMARK.NS", "BSE": "532720.BO", "sector": "Pharma"},
    "Global Health": {"NSE": "GLOBALHEALTH.NS", "BSE": "543322.BO", "sector": "Healthcare"},
    "Godfrey Phillips": {"NSE": "GODFRYPHLP.NS", "BSE": "500039.BO", "sector": "Tobacco"},
    "Gokaldas Exports": {"NSE": "GOKEX.NS", "BSE": "500168.BO", "sector": "Textiles"},
    "Gopal Snacks": {"NSE": "GOPALKRISH.NS", "BSE": "543440.BO", "sector": "Food"},
    "Granules India": {"NSE": "GRANULES.NS", "BSE": "532482.BO", "sector": "Pharma"},
    "HFCL Limited": {"NSE": "HFCL.NS", "BSE": "500183.BO", "sector": "Telecom"},
    "Himadri Speciality": {"NSE": "HSCL.NS", "BSE": "543482.BO", "sector": "Chemicals"},
    "Indiamart Intermesh": {"NSE": "INDIAMART.NS", "BSE": "544012.BO", "sector": "E-commerce"},
    "Indian Renewable Energy": {"NSE": "IREDA.NS", "BSE": "543257.BO", "sector": "Energy"},
    "Indoco Remedies": {"NSE": "INDOCORE.NS", "BSE": "533317.BO", "sector": "Pharma"},
    "Indian Bank": {"NSE": "INDIANB.NS", "BSE": "532814.BO", "sector": "Banking"},
    "IndusInd Bank": {"NSE": "INDUSINDBK.NS", "BSE": "532187.BO", "sector": "Banking"},
    "Jindal Saw": {"NSE": "JINDALSAW.NS", "BSE": "500378.BO", "sector": "Steel"},
    "Jio Platforms": {"NSE": "JIOPLATFORMS.NS", "BSE": "543770.BO", "sector": "Telecom"},
    "KEI Industries": {"NSE": "KEI.NS", "BSE": "517569.BO", "sector": "Electrical"},
    "KFin Technologies": {"NSE": "KFINTECH.NS", "BSE": "543276.BO", "sector": "Finance"},
    "KPR Mill": {"NSE": "KPRMILL.NS", "BSE": "532889.BO", "sector": "Textiles"},
    "LaOpala": {"NSE": "LAOPALA.NS", "BSE": "526343.BO", "sector": "Consumer Goods"},
    "L&T Technology Services": {"NSE": "LTTS.NS", "BSE": "540115.BO", "sector": "IT"},
    "Mahindra Holidays": {"NSE": "MHRIL.NS", "BSE": "500182.BO", "sector": "Hospitality"},
    "Mahindra Lifespace": {"NSE": "MAHLIFE.NS", "BSE": "535789.BO", "sector": "Real Estate"},
    "Manappuram Finance": {"NSE": "MANAPPURAM.NS", "BSE": "531213.BO", "sector": "Finance"},
    "Metropolis Healthcare": {"NSE": "METROPOLIS.NS", "BSE": "542650.BO", "sector": "Healthcare"},
    "Minda Corporation": {"NSE": "MINDAIND.NS", "BSE": "538962.BO", "sector": "Auto Components"},
    "Mold-Tek Packaging": {"NSE": "MOLDTECH.NS", "BSE": "543640.BO", "sector": "Packaging"},
    "Mphasis": {"NSE": "MPHASIS.NS", "BSE": "526299.BO", "sector": "IT"},
    "Narayana Hrudayalaya": {"NSE": "NH.NS", "BSE": "539551.BO", "sector": "Healthcare"},
    "NLC India": {"NSE": "NLCINDIA.NS", "BSE": "513683.BO", "sector": "Energy"},
    "Oberoi Realty": {"NSE": "OBEROIREALTY.NS", "BSE": "533273.BO", "sector": "Real Estate"},
    "One 97 Communications": {"NSE": "PAYTM.NS", "BSE": "543390.BO", "sector": "Fintech"},
    "PB Fintech": {"NSE": "PBFI.NS", "BSE": "543386.BO", "sector": "Finance"},
    "Patanjali Foods": {"NSE": "PATANJALI.NS", "BSE": "533271.BO", "sector": "Food"},
    "Piramal Pharma": {"NSE": "PPLPHARMA.NS", "BSE": "543489.BO", "sector": "Pharma"},
    "Poonawalla Fincorp": {"NSE": "POONAWALLA.NS", "BSE": "543335.BO", "sector": "Finance"},
    "Prataap Snacks": {"NSE": "PRATAPSNACKS.NS", "BSE": "543678.BO", "sector": "Food"},
    "RBL Bank": {"NSE": "RBLBANK.NS", "BSE": "500243.BO", "sector": "Banking"},
    "Relaxo Footwears": {"NSE": "RELAXO.NS", "BSE": "533587.BO", "sector": "Consumer Goods"},
    "RITES Limited": {"NSE": "RITES.NS", "BSE": "541556.BO", "sector": "Engineering"},
    "Rossari Biotech": {"NSE": "ROSSARI.NS", "BSE": "543500.BO", "sector": "Chemicals"},
    "SBI Life": {"NSE": "SBILIFE.NS", "BSE": "540719.BO", "sector": "Insurance"},
    "Schaeffler India": {"NSE": "SCHAEFFLER.NS", "BSE": "505790.BO", "sector": "Engineering"},
    "Sharda Cropchem": {"NSE": "SHARDACROP.NS", "BSE": "500387.BO", "sector": "Agrochemicals"},
    "Shoppers Stop": {"NSE": "SHOPERSTOP.NS", "BSE": "532638.BO", "sector": "Retail"},
    "Solar Industries": {"NSE": "SOLARINDS.NS", "BSE": "523  ?", "sector": "Defense"},
    "SpiceJet": {"NSE": "SPICEJET.NS", "BSE": "500285.BO", "sector": "Aviation"},
    "Star Health": {"NSE": "STARHEALTH.NS", "BSE": "543412.BO", "sector": "Insurance"},
    "Sundaram Finance": {"NSE": "SUNDARMFIN.NS", "BSE": "590071.BO", "sector": "Finance"},
    "Sundram Fasteners": {"NSE": "SUNDRMFAST.NS", "BSE": "500387.BO", "sector": "Auto Components"},
    "Suprajit Engineering": {"NSE": "SUPRAJIT.NS", "BSE": "543333.BO", "sector": "Auto Components"},
    "Tata Communications": {"NSE": "TATACOMM.NS", "BSE": "532812.BO", "sector": "Telecom"},
    "Tata Power": {"NSE": "TATAPOWER.NS", "BSE": "532779.BO", "sector": "Energy"},
    "Tata Teleservices": {"NSE": "TTML.NS", "BSE": "500483.BO", "sector": "Telecom"},
    "Tejas Networks": {"NSE": "TEJASNET.NS", "BSE": "543942.BO", "sector": "Telecom"},
    "The Phoenix Mills": {"NSE": "PHOENIXLTD.NS", "BSE": "503100.BO", "sector": "Real Estate"},
    "Timken India": {"NSE": "TIMKEN.NS", "BSE": "517206.BO", "sector": "Engineering"},
    "Trent Limited": {"NSE": "TRENT.NS", "BSE": "500251.BO", "sector": "Retail"},
    "Tube Investments": {"NSE": "TIINDIA.NS", "BSE": "540716.BO", "sector": "Engineering"},
    "United Spirits": {"NSE": "UNITEDSPIRITS.NS", "BSE": "500216.BO", "sector": "Beverages"},
    "V-Guard Industries": {"NSE": "VGUARD.NS", "BSE": "532953.BO", "sector": "Consumer Durables"},
    "Varun Beverages": {"NSE": "VARUNBEVERAGES.NS", "BSE": "540180.BO", "sector": "Food"},
    "Vijaya Diagnostics": {"NSE": "VIJAYAHR.NS", "BSE": "543311.BO", "sector": "Healthcare"},
    "Vipul Limited": {"NSE": "VIPULLTD.NS", "BSE": "523690.BO", "sector": "Real Estate"},
    "Wockhardt": {"NSE": "WOCKPHARMA.NS", "BSE": "532300.BO", "sector": "Pharma"},
    "Yes Bank": {"NSE": "YESBANK.NS", "BSE": "532648.BO", "sector": "Banking"},
    "Zota Health": {"NSE": "ZOTA.NS", "BSE": "543252.BO", "sector": "Healthcare"},
}

for _name, _info in EXTENDED_COMPANIES.items():
    if _name not in ALL_INDIAN_COMPANIES:
        ALL_INDIAN_COMPANIES[_name] = _info

# Curated featured companies (display prominently on the dashboard)
FEATURED_COMPANIES = [
    "Reliance Industries Limited",
    "Tata Consultancy Services",
    "Infosys Limited",
    "HDFC Bank Limited",
    "ICICI Bank Limited",
    "Hindustan Unilever",
    "Bharti Airtel Limited",
    "Kotak Mahindra Bank",
    "Larsen & Toubro",
    "Bajaj Finance",
    "Maruti Suzuki India",
    "Asian Paints India",
    "ITC Limited",
    "State Bank of India",
    "Nestlé India Limited",
    "3M India Limited",
    "ACC Limited",
    "Adani Enterprises",
    "Adani Ports",
    "Adani Power"
]

# Initialize the validated list from the core company set.
VALIDATED_COMPANIES = [
    '3M India Limited', 'ACC Limited', 'Adani Enterprises', 'Adani Ports', 'Adani Power',
    'Ambuja Cements', 'Apollo Hospitals', 'Ashok Leyland', 'Asian Paints India', 'Axis Bank',
    'Axis Bank Limited', 'BGR Energy', 'Bajaj Finance', 'Bajaj Finserv', 'Bank of Baroda',
    'Bank of India', 'Berger Paints', 'Bharat Petroleum', 'Bharati V-Art', 'Bharti Airtel Limited',
    'Biocon Limited', 'Blue Dart Express', 'Bosch Limited', 'Britannia Industries', 'Cipla Limited',
    'Coal India Limited', 'Colgate Palmolive', 'Container Corporation', 'DCM Shriram', 'Dabur India',
    'Deepak Fertilizers', "Divi's Laboratories", 'Dixon Technologies', "Dr. Reddy's Laboratories", 'Escorts Limited',
    'Exicom Tele Systems', 'Federal Bank', 'Gail India Limited', 'Genesys International', 'Gillette India',
    'Glaxo Smithkline', 'Go Digit Insurance', 'Godrej Industries', 'Goldtech Pharmaceuticals', 'Graphite India',
    'Grasim Industries', 'Greaves Leasing', 'Greenply Industries', 'Grindwell Norton', 'HCL Technologies',
    'HDFC Bank Limited', 'Hero MotoCorp', 'Hi-Tech Pharma', 'Hindalco Industries', 'Hindustan Aeronautics',
    'Hindustan Copper', 'Hindustan Motors', 'Hindustan Petroleum', 'Hindustan Unilever', 'Hindusthan Industries',
    'Home First Finance', 'Hyundai Motor', 'ICICI Bank Limited', 'ICICI Prudential', 'ITC Limited',
    'Ideaforge Technology', 'Indian Hotels', 'Indian Metals', 'Indian Oil', 'Indian Oil Corporation',
    'Indigo Airlines', 'Indraprastha Gas', 'Indus Towers', 'IndusInd Bank', 'Infosys Limited',
    'Integrated Infratech', 'Intel India', 'InterGlobe Aviation', 'Interglobe Finance', 'Ion Exchange',
    'JSW Steel Limited', 'Kotak Mahindra Bank', 'Larsen & Toubro', 'Lupin Limited', 'Maruti Suzuki India',
    'NTPC Limited', 'Nestlé India Limited', 'Oil and Natural Gas', 'Power Grid Corporation', 'Reliance Industries Limited',
    'Shree Cement', 'State Bank of India', 'Sun Pharmaceutical', 'Tata Consultancy Services', 'Tata Steel Limited',
    'Tech Mahindra', 'Ultratech Cement', 'Wipro Limited', 'Avenue Supermarts', 'Bajaj Auto Limited',
    'Bharat Forge', 'Bharat Petroleum', 'Bharti Airtel Limited', 'Borosil Limited', 'Canara Bank',
    'Ceat Limited', 'Cognizant Technology', 'Contech Solutions', 'Dixon Technologies', 'Emami Limited',
    'Eicher Motors', 'Federal Bank', 'Finolex Cables', 'GMR Infrastructure', 'Godrej Properties',
    'Gujarat Gas', 'Havells India', 'HDFC Life Insurance', 'HDFC Asset Management', 'Hindustan Aeronautics',
    'Hindustan Petroleum Corporation', 'Hindustan Shipyard', 'HSBC India', 'ICICI Securities', 'Indian Bank',
    'Indian Hotels', 'Indian Oil', 'Indigo Paints', 'Indus Towers', 'Jubilant FoodWorks', 'JSW Energy',
    'Kansai Nerolac Paints', 'LIC India', 'LTIMindtree', 'L&T Technology Services', 'Mahindra & Mahindra',
    'Marico Limited', 'Motherson Sumi Systems', 'Muthoot Finance', 'NHPC Limited', 'Oil India',
    'PVR INOX', 'Pidilite Industries', 'Power Finance Corporation', 'Procter & Gamble Hygiene',
    'SBI Cards and Payment Services', 'SBI Life Insurance', 'Siemens India', 'Steel Authority of India',
    'Tata Consumer Products', 'Tata Elxsi', 'Tata Motors Limited', 'Tata Power Company', 'Titan Company Limited',
    'Torrent Pharmaceuticals', 'TVS Motor Company', 'UPL Limited', 'Voltas Limited', 'Zee Entertainment Enterprises',
    'Zomato Limited', 'Zydus Lifesciences'
]

# Expand the registry to a larger live-data-friendly set from the master database.
TARGET_COMPANY_COUNT = 450
for company_name in ALL_INDIAN_COMPANIES:
    if company_name not in VALIDATED_COMPANIES:
        ticker_info = ALL_INDIAN_COMPANIES[company_name]
        if ticker_info.get('NSE'):
            VALIDATED_COMPANIES.append(company_name)
    if len(VALIDATED_COMPANIES) >= TARGET_COMPANY_COUNT:
        break

VALIDATED_COMPANIES = VALIDATED_COMPANIES[:TARGET_COMPANY_COUNT]
VALIDATED_COMPANIES.extend(
    [name for name in ADDITIONAL_COMPANIES.keys() if name not in VALIDATED_COMPANIES]
)
VALIDATED_COMPANIES = VALIDATED_COMPANIES[:TARGET_COMPANY_COUNT]
VALIDATED_COMPANIES.extend(
    [name for name in EXTENDED_COMPANIES.keys() if name not in VALIDATED_COMPANIES]
)
VALIDATED_COMPANIES = VALIDATED_COMPANIES[:TARGET_COMPANY_COUNT]

# Merge additional candidates from data/additional_companies.json if present
import json as _json
from pathlib import Path as _Path
_add_file = _Path(__file__).resolve().parent / 'data' / 'additional_companies.json'
if _add_file.exists():
    try:
        with open(str(_add_file), 'r', encoding='utf-8') as _f:
            _extra = _json.load(_f)
            # Only add companies that are not already present
            for _name, _tick in _extra.items():
                if _name not in ALL_INDIAN_COMPANIES:
                    ALL_INDIAN_COMPANIES[_name] = _tick
    except Exception:
        pass

# Merge the verified Yahoo-backed catalog and prioritize it in the live dashboard registry.
_verified_catalog_path = _Path(__file__).resolve().parent / 'data' / 'yahoo_live_companies.json'
_verified_catalog = {}
if _verified_catalog_path.exists():
    try:
        with open(str(_verified_catalog_path), 'r', encoding='utf-8') as _f:
            _verified_raw = _json.load(_f)
            for _name, _tick_info in _verified_raw.items():
                _normalized = {
                    'NSE': _tick_info.get('NSE') or _tick_info.get('nse'),
                    'BSE': _tick_info.get('BSE') or _tick_info.get('bse', '999999999.BO'),
                    'sector': _tick_info.get('sector', 'General')
                }
                if _normalized['NSE']:
                    ALL_INDIAN_COMPANIES[_name] = _normalized
                    _verified_catalog[_name] = _normalized
    except Exception:
        pass

# Build the active registry from the verified live-supported catalog when available.
_live_supported_catalog_path = _Path(__file__).resolve().parent / 'data' / 'live_supported_companies.json'
_live_supported_names = []
if _live_supported_catalog_path.exists():
    try:
        with open(str(_live_supported_catalog_path), 'r', encoding='utf-8') as _f:
            _loaded_names = _json.load(_f)
            if isinstance(_loaded_names, list):
                _live_supported_names = [name for name in _loaded_names if name in ALL_INDIAN_COMPANIES]
    except Exception:
        _live_supported_names = []

if _live_supported_names:
    active_company_names = [name for name in _live_supported_names if name in ALL_INDIAN_COMPANIES and not is_blocked_company_name(name)]
else:
    active_company_names = [name for name in VALIDATED_COMPANIES if name in ALL_INDIAN_COMPANIES and not is_blocked_company_name(name)]

INDIAN_COMPANIES = {
    name: ALL_INDIAN_COMPANIES[name]
    for name in active_company_names
    if name in ALL_INDIAN_COMPANIES
}

# Ensure featured list only includes validated/available companies and removes blocked names
FEATURED_COMPANIES = [c for c in FEATURED_COMPANIES if c in INDIAN_COMPANIES and not is_blocked_company_name(c)]

# ==================== DATA PATHS ====================
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = str(PROJECT_ROOT / "data")
MODEL_PATH = str(PROJECT_ROOT / "models")
CACHE_PATH = str(PROJECT_ROOT / ".streamlit_cache")
AVAILABILITY_CACHE_FILE = str(PROJECT_ROOT / "data" / "company_availability.json")
AVAILABILITY_CACHE_TTL = 24 * 60 * 60  # 24 hours

# ==================== API SETTINGS ====================
DATA_FETCH_INTERVAL = 300  # seconds (5 minutes)
HISTORICAL_DAYS = 750  # ~3 years of data for training

# ==================== DISPLAY SETTINGS ====================
DECIMAL_PLACES = 2
CHART_HEIGHT = 500
CHART_WIDTH = 1200

# ==================== RECOMMENDATIONS ====================
RECOMMENDATIONS = {
    "BUY": "🟢 BUY - Price expected to increase",
    "HOLD": "🟡 HOLD - Price expected to remain stable",
    "SELL": "🔴 SELL - Price expected to decrease",
}

RISK_LEVELS = {
    "LOW": "🟢 Low Risk",
    "MEDIUM": "🟡 Medium Risk",
    "HIGH": "🔴 High Risk",
}

# ==================== CONFIDENCE THRESHOLDS ====================
CONFIDENCE_THRESHOLDS = {
    "high": 0.75,
    "medium": 0.50,
    "low": 0.25,
}

# ==================== FEATURE IMPORTANCE GUIDE ====================
FEATURE_INFO = {
    "MA10": "10-day Moving Average - Short term trend",
    "MA20": "20-day Moving Average - Medium term trend",
    "RSI": "Relative Strength Index - Momentum indicator (0-100)",
    "MACD": "Moving Average Convergence Divergence - Trend signal",
    "MACD_Signal": "Signal line of MACD",
    "MACD_Hist": "Histogram difference between MACD and Signal",
    "BB_High": "Bollinger Band Upper - Resistance level",
    "BB_Low": "Bollinger Band Lower - Support level",
    "Daily_Return": "Percentage change in daily price",
    "Volatility": "Standard deviation of returns",
}

# ==================== ERROR MESSAGES ====================
ERRORS = {
    "no_data": "⚠️ No data available for this company",
    "model_not_found": "⚠️ Model not trained for this company",
    "invalid_ticker": "⚠️ Invalid ticker symbol",
    "api_error": "⚠️ Error fetching data from Yahoo Finance",
}

# ==================== SUCCESS MESSAGES ====================
SUCCESS_MESSAGES = {
    "data_loaded": "✅ Data loaded successfully",
    "model_trained": "✅ Model trained successfully",
    "prediction_made": "✅ Prediction completed",
}
