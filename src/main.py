from product_scraper.get_product_data import get_product_data
from product_scraper.export_product_data import export_product_data
from product_scraper.crawler import crawl_all_products
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import time
import argparse

def process_product(product: Dict[str, str]) -> None:
    """Process a single product"""
    try:
        # Get product data
        product_data = get_product_data(product['code'], product['name'])
        if product_data:
            export_product_data(product_data)
    except Exception as e:
        print(f"❌ Error processing product {product['code']}: {e}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Baldor Product Scraper')
    parser.add_argument('--limit', type=int, default=10, help='Limit the number of products to process (default: 10)')
    args = parser.parse_args()

    # Get all product IDs
    print("Starting product discovery...")
    crawled_products = crawl_all_products(limit=args.limit)

    # Delete output directory if it exists
    clear_folder('output')

    # Number of concurrent threads (adjust as needed)
    max_workers = 10
    
    print(f"\n🔄 Processing {len(crawled_products)} products using {max_workers} threads...")
    start_time = time.time()
    
    # Process products in parallel using threads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_product = {
            executor.submit(process_product, product): product 
            for product in crawled_products
        }
        
        completed = 0
        for future in as_completed(future_to_product):
            product = future_to_product[future]
            completed += 1
            try:
                future.result()
                print(f"✅ Processed {completed}/{len(crawled_products)}: {product['code']}")
            except Exception as e:
                print(f"❌ Failed to process {product['code']}: {e}")
    
    end_time = time.time()
    print(f"\n✅ All products processed in {end_time - start_time:.2f} seconds!")

def clear_folder(folder_path):
    """
    Delete all files and subfolders in the specified folder,
    but keep the folder itself.
    """
    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Delete file or symlink
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Delete folder
        except Exception as e:
            print(f"Failed to delete {item_path}. Reason: {e}")


if __name__ == "__main__":
    main()