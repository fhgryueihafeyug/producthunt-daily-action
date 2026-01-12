import os
import json
import re
from datetime import datetime

def parse_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Date from Title
    # Title format: # PH今日热榜 | 2026-01-12
    title_match = re.search(r'# PH今日热榜 \| (\d{4}-\d{2}-\d{2})', content)
    date_str = title_match.group(1) if title_match else None

    if not date_str:
        # Fallback: try to extract from filename
        filename = os.path.basename(file_path)
        date_match = re.search(r'producthunt-daily-(\d{4}-\d{2}-\d{2})', filename)
        date_str = date_match.group(1) if date_match else "Unknown"

    products = []
    # Split by product sections (starts with ## [rank. Name])
    # using split ensures we capture everything
    sections = re.split(r'\n## ', content)
    
    # The first section is the header, skip it
    for section in sections[1:]:
        product = {}
        
        # Extract Name and Link
        # Format: [1. Elser AI](https://...)
        name_match = re.match(r'\[(\d+)\.\s+(.*?)\]\((.*?)\)', section)
        if name_match:
            product['rank'] = int(name_match.group(1))
            product['name'] = name_match.group(2)
            product['url'] = name_match.group(3)
        
        # Extract Tagline
        tagline_match = re.search(r'\*\*标语\*\*：(.*?)\n', section)
        if tagline_match:
            product['tagline'] = tagline_match.group(1).strip()
            
        # Extract Description
        desc_match = re.search(r'\*\*介绍\*\*：(.*?)\n', section)
        if desc_match:
            product['description'] = desc_match.group(1).strip()
            
        # Extract Image
        img_match = re.search(r'!\[.*?\]\((.*?)\)', section)
        if img_match:
            product['image_url'] = img_match.group(1).split('?')[0] # Remove query params if needed, or keep them
            
        # Extract Votes
        votes_match = re.search(r'\*\*票数\*\*: 🔺(\d+)', section)
        if votes_match:
            product['votes_count'] = int(votes_match.group(1))
            
        # Extract Featured
        featured_match = re.search(r'\*\*是否精选\*\*：(.*?)\n', section)
        if featured_match:
            product['featured'] = featured_match.group(1).strip() == '是'
            
        # Extract Created At
        created_match = re.search(r'\*\*发布时间\*\*：(.*?)\n', section)
        if created_match:
            product['created_at'] = created_match.group(1).strip()
            
        products.append(product)

    return {
        'date': date_str,
        'products': products
    }

def main():
    data_dir = 'data'
    json_output_dir = 'data'
    
    all_days = []

    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist.")
        return

    for filename in os.listdir(data_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(data_dir, filename)
            print(f"Processing {filename}...")
            
            try:
                data = parse_markdown_file(file_path)
                
                # Save individual JSON
                json_filename = filename.replace('.md', '.json')
                json_path = os.path.join(json_output_dir, json_filename)
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Add to index list
                # We need summary info for the index card
                if data['products']:
                    top_product = data['products'][0]
                    summary = {
                        'date': data['date'],
                        'title': f"PH今日热榜 | {data['date']}",
                        'top_product': {
                            'name': top_product.get('name'),
                            'tagline': top_product.get('tagline'),
                            'image_url': top_product.get('image_url')
                        },
                        'products_count': len(data['products']),
                        'filename': json_filename
                    }
                    all_days.append(summary)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Sort by date descending
    all_days.sort(key=lambda x: x['date'], reverse=True)

    # Save index.json
    index_path = os.path.join(data_dir, 'index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(all_days, f, ensure_ascii=False, indent=2)
    
    print(f"Generated index.json with {len(all_days)} entries.")

if __name__ == '__main__':
    main()
