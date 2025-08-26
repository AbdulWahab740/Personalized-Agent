from langchain.tools import tool
import pandas as pd
from automation.linkedin_content_automation import LinkedInContentAutomation
import streamlit as st
automation = LinkedInContentAutomation()

@tool
@st.cache_data(ttl=3600) 
def load_engagement(file):
        """Load engagement data from an Excel file."""
        try:
            engagement_df = pd.read_excel(file,sheet_name="ENGAGEMENT")
            engagement_df["Date"] = pd.to_datetime(engagement_df["Date"])
            engagement_df = engagement_df.sort_values("Date")
            if 'Date' in engagement_df.columns:
                engagement_df['Date'] = pd.to_datetime(engagement_df['Date'], errors='coerce')

            if 'Engagements' in engagement_df.columns:
                engagement_df['Engagements'] = pd.to_numeric(engagement_df['Engagements'], errors='coerce')

            df_monthly = engagement_df.groupby(engagement_df['Date'].dt.to_period("M")).agg({
                'Engagements': 'sum',
                'Impressions': 'sum'
            }).reset_index()

            # Calculate growth rates month-to-month
            df_monthly['Engagement Growth %'] = df_monthly['Engagements'].pct_change() * 100
            df_monthly['Impression Growth %'] = df_monthly['Impressions'].pct_change() * 100
            return df_monthly.to_dict(orient="records")
        except Exception as e:
            print("Could not load the file", e)
            return {"error": f"Failed to load engagement data: {str(e)}"}

@st.cache_data(ttl=3600) 
def load_top_posts(file):
        """Load top posts data from an Excel file."""
        try:
            # Skip the first 2 rows (header text and empty row) and use row 3 as column names
            df_top_posts = pd.read_excel(file, sheet_name="TOP POSTS", skiprows=2)
            print(f"DEBUG: Column names in TOP POSTS sheet: {list(df_top_posts.columns)}")
            
            # Clean column names (remove extra spaces)
            df_top_posts.columns = df_top_posts.columns.str.strip()
            
            # Map lowercase -> original column for case-insensitive matching
            lower_to_orig = {c.lower(): c for c in df_top_posts.columns}
            def find_col(candidates):
                for name in candidates:
                    key = name.lower()
                    if key in lower_to_orig:
                        return lower_to_orig[key]
                # try relaxed contains search
                for key, orig in lower_to_orig.items():
                    if any(token in key for token in candidates):
                        return orig
                return None

            # Candidate names
            engagement_candidates = ["engagements", "engagement", "interactions"]
            impression_candidates = ["impressions", "impression", "views"]

            engagement_col = find_col(engagement_candidates)
            impression_col = find_col(impression_candidates)

            # Coerce numeric (handle commas/strings)
            def to_num(series):
                return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False).str.extract(r"([-+]?[0-9]*\.?[0-9]+)", expand=False), errors='coerce')

            if engagement_col:
                df_top_posts[engagement_col] = to_num(df_top_posts[engagement_col])
            if impression_col:
                df_top_posts[impression_col] = to_num(df_top_posts[impression_col])

            # Sorting logic: prefer engagements, then impressions as tiebreaker
            if engagement_col and impression_col:
                df_top_posts = df_top_posts.sort_values(by=[engagement_col, impression_col], ascending=[False, False])
                print(f"DEBUG: Sorting by '{engagement_col}' then '{impression_col}' (desc)")
            elif engagement_col:
                df_top_posts = df_top_posts.sort_values(by=engagement_col, ascending=False)
                print(f"DEBUG: Sorting by '{engagement_col}' (desc)")
            elif impression_col:
                df_top_posts = df_top_posts.sort_values(by=impression_col, ascending=False)
                print(f"DEBUG: Sorting by '{impression_col}' (desc)")
            else:
                print("DEBUG: No engagement/impression column found; returning unsorted data")
            
            # Remove rows with all NaN values
            df_top_posts = df_top_posts.dropna(how='all')
            # Optional: drop rows where both metrics are NaN
            if engagement_col or impression_col:
                cols = [c for c in [engagement_col, impression_col] if c]
                df_top_posts = df_top_posts.dropna(subset=cols, how='all')
            
            result = df_top_posts.head(10).to_dict(orient="records")
            print(f"DEBUG: First top post data: {result[0] if result else 'No data'}")
            print(f"DEBUG: Total posts loaded: {len(result)}")
            return result

        except Exception as e:
            print("Could not load the file", e)
            return {"error": f"Failed to load top posts data: {str(e)}"}

@tool
@st.cache_data(ttl=3600) 
def load_overall_performance(file):
        """Load overall performance data from an Excel file."""
        try:
            df_overall = pd.read_excel(file, sheet_name="DISCOVERY")
            return df_overall.to_dict(orient="records")
            
        except Exception as e:
            print("Could not load the file", e)
            return {"error": f"Failed to load overall performance data: {str(e)}"}
    
@tool 
@st.cache_data(ttl=3600) 
def load_demographics(file):
        """Load demographics data from an Excel file."""
        try:
            demographics_df = pd.read_excel(file, sheet_name="DEMOGRAPHICS")
            demographics_df["Percentage"] = pd.to_numeric(demographics_df["Percentage"], errors='coerce')
            demographics_df = demographics_df.sort_values(by="Percentage", ascending=False)
            return demographics_df.to_dict(orient="records")
        except Exception as e:
            print("Could not load the file", e)
            return {"error": f"Failed to load demographics data: {str(e)}"}

