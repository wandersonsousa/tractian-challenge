import requests
import json
from typing import List, Dict
import time

base_url = "https://www.baldor.com/api/products"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}
#https://www.baldor.com/api/products?include=results&language=en-US&include=filters&include=category&pageSize=10
def get_categories() -> List[Dict]:
    """Get all main product categories"""
    params = {
        "include": "results",
        "include": "category",
        "language": "en-US",
        "pageSize": "1000" # TODO: for now there is no more than 1000 categories, but we can change this if needed
    }
    
    response = requests.get(base_url, params=params, headers=headers)

    data = response.json()
    categories = []
    
    # Extract categories, getting only id and text, that are other fields we can use later on if needed
    if 'category' in data:
        if 'children' in data['category']:
            for category in data['category']['children']:
                cat_data = {
                    "id": category.get('id'),
                    "text": category.get('text'),
                }
                categories.append(cat_data)
    
    return categories
   

def get_subcategories(category_id: str) -> List[Dict]:
    """Get subcategories for a given category ID"""
    params = {
        "include": "category",
        "language": "en-US",
        "pageSize": "1000", # TODO: for now there is no more than 1000 subcategories, but we can change this if needed
        "category": category_id
    }
    
    response = requests.get(base_url, params=params, headers=headers)

    data = response.json()
    subcategories = []
    
    # Extract subcategories from the filters section
    if 'category' in data:
        if 'children' in data['category']:
            for subcategory in data['category']['children']:
                subcat_data = {
                    "id": subcategory.get('id'),
                    "text": subcategory.get('text'),
                }
                subcategories.append(subcat_data)
    
    return subcategories
   

def get_products(category_id: str, page_size: int = 100, page_index: int = 0) -> List[Dict]:
    """Get all products for a given category ID"""
    params = {
        "include": "results",
        "language": "en-US",
        "pageSize": page_size,
        "pageIndex": page_index,
        "category": category_id
    }
    
    response = requests.get(base_url, params=params, headers=headers)

    data = response.json()
    products = []
    
    # Extract products from the results section
    if 'results' in data:
        if 'matches' in data['results']:
            for product in data['results']['matches']:
                product_data = {
                    "code": product.get('code'),
                    "description": product.get('description'),
                    "upc": product.get('upc')
                }
                products.append(product_data)
    
    return products
   
def crawl_all_products(limit: int = None) -> List[str]:
    """Crawl all categories and subcategories to get all product IDs
    
    Args:
        limit (int, optional): Maximum number of products to scrape. If None, scrapes all products.
    """
    all_products = []
    products_scraped = 0
    
    # Get main categories
    categories = get_categories()
    print(f"Found {len(categories)} main categories")
    
    for category in categories:
        if limit and products_scraped >= limit:
            break
            
        print(f"\nProcessing category: {category['text']} (ID: {category['id']})")
        
        # Get subcategories
        subcategories = get_subcategories(category['id'])
        print(f"Found {len(subcategories)} subcategories")
        
        for subcategory in subcategories:
            if limit and products_scraped >= limit:
                break
                
            print(f"\nProcessing subcategory: {subcategory['text']} (ID: {subcategory['id']})")
            
            # Get products for this subcategory
            products = get_products(subcategory['id'])
            print(f"Found {len(products)} products")
            
            # Add product codes to our list, respecting the limit
            remaining = limit - products_scraped if limit else len(products)
            products_to_add = products[:remaining]
            all_products.extend([{
                "code": p['code'],
                "name": f"{subcategory['text']} - {category['text']}",
            } for p in products_to_add])
            products_scraped += len(products_to_add)
            
            # Be nice to the server
            time.sleep(1)
        
        # Be nice to the server
        time.sleep(2)
 
    return all_products 