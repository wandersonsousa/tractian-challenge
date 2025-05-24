import streamlit as st
import pandas as pd
import json
import os
import shutil
from product_scraper.get_product_data import get_product_data
from product_scraper.export_product_data import export_product_data
from product_scraper.crawler import crawl_all_products
import time
from concurrent.futures import ThreadPoolExecutor
import threading

st.set_page_config(
    page_title="Baldor.com Scraper",
    page_icon="🔍",
    layout="wide"
)

if 'scraping_progress' not in st.session_state:
    st.session_state.scraping_progress = 0
if 'scraping_status' not in st.session_state:
    st.session_state.scraping_status = ""

def update_progress(progress, status):
    st.session_state.scraping_progress = progress
    st.session_state.scraping_status = status

def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  
        except Exception as e:
            st.error(f"Failed to delete {item_path}. Reason: {e}")

def process_product(product):
    try:
        product_data = get_product_data(product['code'], product['name'])
        if product_data:
            export_product_data(product_data)
            return True, product['code']
        return False, product['code']
    except Exception as e:
        return False, f"{product['code']}: {str(e)}"

def bulk_scrape(limit):
    try:
        # Clear output directory before starting
        clear_folder('output')
        
        # Get products to scrape
        products = crawl_all_products(limit=limit)
        total_products = len(products)
        completed = 0
        successful = []
        failed = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_product = {
                executor.submit(process_product, product): product 
                for product in products
            }
            
            for future in future_to_product:
                completed += 1
                success, result = future.result()
                if success:
                    successful.append(result)
                else:
                    failed.append(result)
                update_progress(completed / total_products, f"Processing {completed}/{total_products}")

        return successful, failed
    except Exception as e:
        return [], [str(e)]

# Main UI
st.title("Baldor Product Scraper")
st.markdown("A tool to scrape and analyze Baldor product data")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Single Product Scrape")
    product_id = st.text_input("Product ID", "CEBM3615T-D", key="product_id_input")
    if st.button("Scrape Product", key="single_scrape"):
        with st.spinner("Scraping product data..."):
            try:
                product_data = get_product_data(product_id)
                if product_data:
                    export_product_data(product_data)
                    st.success(f"Successfully scraped product {product_id}")
                    
                    st.subheader("Product Details")
                    st.json(product_data)
                else:
                    st.error(f"Failed to scrape product {product_id}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

with col2:
    st.subheader("Bulk Scrape")
    limit = st.number_input("Number of products to scrape", min_value=1, max_value=100, value=10, key="bulk_limit_input")
    if st.button("Start Bulk Scrape", key="bulk_scrape"):
        st.session_state.scraping_progress = 0
        st.session_state.scraping_status = "Starting..."
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful, failed = bulk_scrape(limit)
        
        if successful:
            st.success(f"Successfully scraped {len(successful)} products")
        if failed:
            st.error(f"Failed to scrape {len(failed)} products")
            st.write("Failed products:", failed)

st.header("Scraped Data")
output_dir = 'output'
if os.path.exists(output_dir):
    json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    if json_files:
        all_products = []
        for json_file in json_files:
            with open(os.path.join(output_dir, json_file), 'r') as f:
                product_data = json.load(f)
                all_products.append(product_data)
        
        df = pd.DataFrame(all_products)
        
        search_term = st.text_input("Search products", "")
        if search_term:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        
        st.dataframe(df)
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="baldor_products.csv",
            mime="text/csv"
        )
    else:
        st.info("No scraped data available yet")
else:
    st.info("Output directory not found") 