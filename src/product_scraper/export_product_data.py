import shutil
import requests 
from lxml import html
import json 
import urllib.parse
import os
import asyncio
import aiohttp
from typing import Dict, Any

async def download_file(session: aiohttp.ClientSession, url: str, file_path: str, headers: Dict[str, str]) -> bool:
    """Download a single file asynchronously"""
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                content = await response.read()
                with open(file_path, 'wb') as f:
                    f.write(content)
                return True
            else:
                print(f"❌ Error downloading {url}: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return False

async def download_all_files(product_data: Dict[str, Any], assets_dir: str, headers: Dict[str, str]) -> Dict[str, str]:
    """Download all files concurrently"""
    assets = {}
    download_tasks = []
    
    # Create subdirectories for different file types
    cad_files_dir = os.path.join(assets_dir, 'cad_files')
    drawings_dir = os.path.join(assets_dir, 'drawings')
    performance_curves_dir = os.path.join(assets_dir, 'performance_curves')
    
    os.makedirs(cad_files_dir, exist_ok=True)
    os.makedirs(drawings_dir, exist_ok=True)
    os.makedirs(performance_curves_dir, exist_ok=True)
    
    async with aiohttp.ClientSession() as session:
        if 'to_download' in product_data:
            for file_key, url in product_data['to_download'].items():
                if not url:
                    continue

                # Determine file extension and target directory based on file type
                if file_key == 'product_image':
                    file_extension = '.jpg'
                    target_dir = assets_dir
                elif file_key.startswith('cad_'):
                    file_extension = os.path.splitext(url)[1] or '.dwg'
                    target_dir = cad_files_dir
                elif file_key.startswith('drawing_'):
                    file_extension = '.pdf'
                    target_dir = drawings_dir
                elif file_key.startswith('performance_curves_'):
                    file_extension = '.pdf'
                    target_dir = performance_curves_dir
                elif file_key == 'info_packet':
                    file_extension = '.pdf'
                    target_dir = assets_dir
                else:
                    file_extension = os.path.splitext(url)[1] or '.pdf'
                    target_dir = assets_dir

                # Create file path
                file_path = os.path.join(target_dir, f"{file_key}{file_extension}")
                
                # Add download task
                task = asyncio.create_task(
                    download_file(session, url, file_path, headers)
                )
                download_tasks.append((file_key, file_path, task))

        # Wait for all downloads to complete
        for file_key, file_path, task in download_tasks:
            success = await task
            if success:
                # Get the relative path from the assets directory
                rel_path = os.path.relpath(file_path, os.path.dirname(assets_dir))
                assets[file_key] = os.path.join('assets', rel_path)

    return assets

# Export product data and assets to files
def export_product_data(product_data):
    # Create output directory structure
    product_id = product_data['product_id']
    output_dir = 'output'
    assets_dir = os.path.join(output_dir, 'assets', product_id)

    # Create directories if they don't exist
    os.makedirs(assets_dir, exist_ok=True)
    
    print(f"📥 Downloading assets for {product_id}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ''AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }   
    
    # Download all files concurrently
    product_data['assets'] = asyncio.run(download_all_files(product_data, assets_dir, headers))

    # Remove to_download field before saving
    if 'to_download' in product_data:
        del product_data['to_download']
    
    # Save product data to JSON
    json_path = os.path.join(output_dir, f'{product_id}.json')

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(product_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Saved product data to {json_path}")

    return True
