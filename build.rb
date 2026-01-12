require 'json'
require 'date'

BASE_DIR = File.expand_path(File.dirname(__FILE__))
DATA_DIR = File.join(BASE_DIR, 'data')

def parse_markdown_file(file_path)
  content = File.read(file_path, encoding: 'utf-8')
  filename = File.basename(file_path)
  
  date_match = filename.match(/producthunt-daily-(\d{4}-\d{2}-\d{2})\.md/)
  date_str = date_match ? date_match[1] : "Unknown Date"
  
  # Split content by products
  parts = content.split("\n## [")
  
  products = []
  
  # Skip the first part (header)
  parts[1..-1].each do |part|
    part = '## [' + part
    
    name_match = part.match(/## \[\d+\. (.*?)\]/)
    tagline_match = part.match(/\*\*标语\*\*：(.*?)\n/)
    desc_match = part.match(/\*\*介绍\*\*：(.*?)\n/)
    url_match = part.match(/\*\*产品网站\*\*.*?\[立即访问\]\((.*?)\)/)
    image_match = part.match(/!\[.*?\]\((.*?)\)/)
    keywords_match = part.match(/\*\*关键词\*\*：(.*?)\n/)
    votes_match = part.match(/\*\*票数\*\*.*?[🔺^](\d+)/)
    rank_match = part.match(/## \[(\d+)\./)
    
    if name_match
      product = {
        "rank" => rank_match ? rank_match[1].to_i : 0,
        "name" => name_match[1],
        "tagline" => tagline_match ? tagline_match[1] : "",
        "description" => desc_match ? desc_match[1] : "",
        "votes_count" => votes_match ? votes_match[1].to_i : 0,
        "image_url" => image_match ? image_match[1] : "",
        "url" => url_match ? url_match[1] : "",
        "keywords" => keywords_match ? keywords_match[1] : ""
      }
      products << product
    end
  end
  
  {
    "date" => date_str,
    "products" => products,
    "filename" => filename # Use md filename as key/id
  }
end

def generate_json_data
  md_files = Dir.glob(File.join(DATA_DIR, 'producthunt-daily-*.md'))
  all_data = []
  
  md_files.each do |md_file|
    begin
      data = parse_markdown_file(md_file)
      all_data << data
    rescue => e
      puts "Error parsing #{md_file}: #{e}"
    end
  end

  # Sort by date descending
  all_data.sort_by! { |x| x['date'] }.reverse!
  
  # Construct response structure
  response_data = {
    "index" => [],
    "details" => {}
  }
  
  all_data.each do |entry|
    key = entry['filename']
    top_product = (entry['products'] && entry['products'].first) || {}
    
    response_data["index"] << {
      "date" => entry['date'],
      "title" => "PH今日热榜 | #{entry['date']}",
      "top_product" => {
        "name" => top_product['name'] || '',
        "tagline" => top_product['tagline'] || '',
        "image_url" => top_product['image_url'] || ''
      },
      "filename" => key
    }
    
    response_data["details"][key] = {
      "date" => entry['date'],
      "products" => entry['products']
    }
  end
  
  # Write to data.json
  output_file = File.join(BASE_DIR, 'data.json')
  File.write(output_file, JSON.generate(response_data))
  puts "Successfully generated data.json at #{output_file}"
end

# Run the generator
generate_json_data
