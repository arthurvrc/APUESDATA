import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>

        /* ---------- GLOBAL UI ---------- */
        body {
            font-family: "Inter", sans-serif;
        }
        .main {
            padding: 2rem;
        }
        h1, h2, h3, h4 {
            font-weight: 700;
            color: #1a1a1a;
        }

        /* ---------- CARDS ---------- */
        .ap-card {
            background: #ffffff;
            border-radius: 14px;
            padding: 1.5rem;
            border: 1px solid #e6e6e6;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            margin-bottom: 1.5rem;
        }

        /* ---------- METRICS ---------- */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 800;
            color: #111;
        }

        [data-testid="stMetricDelta"] {
            font-size: 0.9rem;
            font-weight: 600;
        }

        /* ---------- TABLES ---------- */
        .dataframe {
            border-radius: 12px !important;
        }

        /* ---------- SIDEBAR ---------- */
        section[data-testid="stSidebar"] {
            background-color: #fafafa;
            border-right: 1px solid #eee;
        }
        </style>
    """, unsafe_allow_html=True)


def page_title(title, emoji="⚽"):
    st.markdown(f"""
        <div style="padding: 1rem 0;">
            <h1 style="font-size: 2.4rem; font-weight: 800;">{emoji} {title}</h1>
        </div>
    """, unsafe_allow_html=True)
