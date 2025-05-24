import shutil
import requests 
from lxml import html
import json 
import urllib.parse
import os
import re

# Request product detail page and extract data
def get_product_data(product_id, product_name=''):
    print(f"🚀 Starting Baldor Scraper for {product_id}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ''AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }   
    base_url = "https://www.baldor.com"

    product_page = requests.get(f'{base_url}/catalog/{product_id}', headers=headers)

    if product_page.status_code == 200:
        print(f"✅ Product page for {product_id} fetched successfully.")

        tree = html.fromstring(product_page.text)
        
        # Extract basic data
        product_code = tree.xpath('//meta[@property="og:title"]/@content')[0]
        product_description = tree.xpath('//div[@class="product-description"]/text()')[0]
        product_info_packet = requests.utils.requote_uri( base_url + tree.xpath('//a[@id="infoPacket"]/@href')[0])
        product_image =  requests.utils.requote_uri( base_url + tree.xpath('//img[@class="product-image"]/@data-src')[0])
        product_ship_weight = tree.xpath('//th[contains(., "Ship Weight")]/following-sibling::td[1]/text()')[0]    
        product_upc = tree.xpath('//th[contains(., "UPC")]/following-sibling::td[1]/text()')[0]

        # Extract specs data
        specs = {}  
        spec_rows = tree.xpath('//div[@data-tab="specs"]//div[@class="section detail-table product-overview"]//div[contains(@class, "col")]//div')
        for row in spec_rows:
            label = row.xpath('.//span[@class="label"]/text()')
            value = row.xpath('.//span[@class="value"]/text()')
            
            if label and value:
                label_text = label[0].strip()
                value_text = value[0].strip()
                specs[label_text] = value_text if value_text != "None" else None

        # Extract nameplate data
        nameplate = {}
        nameplate_rows = tree.xpath('//table[@class="nameplate"]//tr')
        for row in nameplate_rows:
            headers = row.xpath('.//th/text()')
            values = row.xpath('.//td/text()')
            
            for i, header in enumerate(headers):
                if i < len(values):
                    header_text = header.strip()
                    value_text = values[i].strip()
                    if header_text and value_text:
                        nameplate[header_text] = value_text
        
        # Extract CAD files and drawings data
        cad_files = []
        drawings_data = []
        cad_section = tree.xpath('//div[@class="section cadfiles"]/@ng-init')
        if cad_section:
            init_text = cad_section[0]

            cad_start_idx = init_text.find('[')
            cad_end_idx = init_text.find("]',")
            if cad_start_idx != -1 and cad_end_idx != -1:
                cad_json_str = init_text[cad_start_idx:cad_end_idx + 1]
                try:
                    cad_data = json.loads(cad_json_str)
                    cad_files = [{
                        'name': item.get('name', ''),
                        'value': item.get('value', ''),
                        'version': item.get('version', ''),
                        'filetype': item.get('filetype', ''),
                        f'cad_{item.get("value", "")}_fileurl': convert_baldor_cad_file_url(item.get('url', '')) if item.get('url', '') else None
                    } for item in cad_data]
                except json.JSONDecodeError as e:
                    print(f"Error parsing CAD files JSON: {e}")

            # Get drawings data
            drawings_start_idx = init_text.find("'[", cad_end_idx)
            if drawings_start_idx != -1:
                drawings_start_idx += 1 
                drawings_end_idx = init_text.rfind("]'", drawings_start_idx)
                if drawings_end_idx != -1:
                    drawings_json_str = init_text[drawings_start_idx:drawings_end_idx + 1]
                    drawings_data = json.loads(drawings_json_str)
                    drawings_items = [
                        {
                            'number': item.get('number', ''),
                            'kind': getDrwKindName(item.get('kind', 0)),
                            f'drawing_{item.get("number", "")}_fileurl': f'{base_url}/api/products/{product_code}/drawings/{item.get("number", "")}',
                            'kind_id': item.get('kind', 0),
                            'material': item.get('material', ''),
                            'description': item.get('description', ''),
                            'url': item.get('url', ''),
                            'type': item.get('type', ''),
                            'revision': item.get('revision', ''),
                        } for item in drawings_data]
                    drawings = drawings_items

        
        # Extract performance data
        performance = {}
        performance_tab = tree.xpath('//div[@data-tab="performance"]')[0]
        
        # Get all performance sections (each voltage configuration)
        performance_sections = performance_tab.xpath('.//h2[contains(text(), "Performance at")]')
        
        for section in performance_sections:
            # Extract voltage configuration from the title
            title = section.text_content().strip()
            # Extract only the voltage value from "Performance at XXX V, ..."
            voltage_match = re.search(r'Performance at (\d+) V', title)
            voltage_config = voltage_match.group(1) if voltage_match else title.replace("Performance at ", "")
            
            performance[voltage_config] = {
                "general_characteristics": {},
                "load_characteristics": {}
            }
            
            current = section.getnext()
            
            # Skip the disclaimer text
            if current.tag == 'em':
                current = current.getnext()
            
            # Process General Characteristics
            if current.tag == 'h3' and "General Characteristics" in current.text_content():
                current = current.getnext()
                if current.tag == 'div' and 'detail-table' in current.get('class', []):
                    for row in current.xpath('.//div[contains(@class, "col")]//div'):
                        label = row.xpath('.//span[@class="label"]/text()')
                        value = row.xpath('.//span[@class="value"]/text()')
                        
                        if label and value:
                            label_text = label[0].strip()
                            value_text = value[0].strip()
                            performance[voltage_config]["general_characteristics"][label_text] = value_text
                
                current = current.getnext()
            
            # Process Load Characteristics
            if current.tag == 'h3' and "Load Characteristics" in current.text_content():
                current = current.getnext()
                if current.tag == 'table' and 'data-table' in current.get('class', []):
                    headers = current.xpath('.//thead//th/text()')
                    rows = current.xpath('.//tbody//tr')
                    
                    for row in rows:
                        metric = row.xpath('.//th[@class="key"]/text()')[0].strip()
                        values = row.xpath('.//td[@class="right"]/text()')
                        
                        performance[voltage_config]["load_characteristics"][metric] = {
                            headers[i].strip(): values[i].strip() if i < len(values) else None
                            for i in range(len(headers))
                        }
            
            # Process Performance Curves if present
            current = current.getnext()
            if current.tag == 'h3' and "Performance Curves" in current.text_content():
                current = current.getnext()
                if current.tag == 'div' and 'drawings' in current.get('class', []):
                    curve_url = current.xpath('.//a/@href')[0]
                    
                    performance[voltage_config]["performance_curves"] = {
                        f"performance_curves_fileurl": curve_url,
                    }

        # Extract parts data
        parts = []
        parts_rows = tree.xpath('//div[@data-tab="parts"]//table[@class="data-table"]//tr')
        for row in parts_rows[1:]:  # Skip header row
            part_number = row.xpath('.//td[@class="key"]/text()')[0].strip()
            description = row.xpath('.//td[2]/text()')[0].strip()
            quantity = row.xpath('.//td[3]/text()')[0].strip()
            
            parts.append({
                'part_number': part_number,
                'description': description,
                'quantity': quantity
            })

        # Collect all downloadable URLs
        to_download = {
            'info_packet': product_info_packet,
            'product_image': product_image,
        }

        # Add CAD files URLs
        for cad_file in cad_files:
            if f'cad_{cad_file["value"]}_fileurl' in cad_file:
                to_download[f'cad_{cad_file["value"]}'] = cad_file[f'cad_{cad_file["value"]}_fileurl']

        # Add drawings URLs
        for drawing in drawings:
            if f'drawing_{drawing["number"]}_fileurl' in drawing:
                to_download[f'drawing_{drawing["number"]}'] = drawing[f'drawing_{drawing["number"]}_fileurl']

        # Add performance curves URLs
        for voltage_config, perf_data in performance.items():
            if 'performance_curves' in perf_data and 'performance_curves_fileurl' in perf_data['performance_curves']:
                to_download[f'performance_curves_{voltage_config}'] = perf_data['performance_curves']['performance_curves_fileurl']

        product = {
            'url': f'{base_url}/catalog/{product_id}',
            'product_id': product_code,
            'name': product_name,
            'description': product_description,
            'ship_weight': product_ship_weight,
            'upc': product_upc,
            'specs': specs,
            'nameplate': nameplate,
            'performance': performance,
            'bom': parts,
            'to_download': to_download
        }    
        
        return product

    print("✅ Scraper finished successfully.")
def convert_baldor_cad_file_url(original_url: str) -> str:
    # The HTML contains only an internal URL for downloading the file. We need to convert it to link this internal URL to the public download API, which works as a proxy to download the files.
    parsed = urllib.parse.urlparse(original_url)
    query_params = urllib.parse.parse_qs(parsed.query)
    comp_id = query_params.get('compId', [None])[0]

    if not comp_id:
        raise ValueError("compId not found in the URL")

    encoded_url = urllib.parse.quote(original_url, safe='')

    download_url = (
        f"https://www.baldor.com/api/products/download/"
        f"?value={urllib.parse.quote(comp_id)}&url={encoded_url}"
    )
    return download_url
def getDrwKindName(kind: int):
    # Function cloned from the js files of the original website
    if kind == 0:
        return 'Dimension Sheet'
    elif kind == 1:
        return 'Connection Diagram'
    elif kind == 2:
        return 'ElectricalDesign'
    elif kind == 3:
        return 'Literature'
    elif kind == 4:
        return 'Other'