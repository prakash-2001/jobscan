from flask import Flask, request, jsonify, render_template
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        return f"Request failed: {e}"

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

def parse_jobs(html, keyword):
    soup = BeautifulSoup(html, 'html.parser')
    job_elements = []
    
    # Customize these selectors based on the website's HTML structure
    for job in soup.find_all(['h2', 'h3', 'p']):  # Example tags
        if keyword.lower() in job.get_text().lower():
            job_elements.append(job.get_text())
    
    return job_elements

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
async def search_jobs():
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    urls = [
        "https://www.capgemini.com/in-en/careers/",
        "https://www.oracle.com/in/careers/opportunities/engineering-development/",
        "https://careers.adobe.com/us/en"
    ]
    
    print("Searching...")
    results = await fetch_all(urls)
    
    found = False
    response_data = []

    for idx, html in enumerate(results):
        jobs = parse_jobs(html, keyword)
        if jobs:
            found = True
            response_data.append({
                "url": urls[idx],
                "jobs": jobs
            })

    if not found:
        return jsonify({"message": "No jobs found for the keyword"}), 200

    return jsonify({"results": response_data}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
