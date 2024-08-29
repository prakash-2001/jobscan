from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pydantic import BaseModel
import os
from typing import List, Dict

app = FastAPI()

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

    keyword_lower = keyword.lower()  # Convert keyword to lowercase for case-insensitive comparison

    # Customize these selectors based on the website's HTML structure
    for job in soup.find_all(['h2', 'h3', 'p']):  # Example tags
        job_text = job.get_text().lower()  # Convert job text to lowercase
        if keyword_lower in job_text:
            job_elements.append(job.get_text())

    return job_elements

@app.get("/")
async def index():
    return render_template('index.html')

@app.get("/search")
async def search_jobs(keyword: str):
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

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
        return JSONResponse(content={"message": "No jobs found for the keyword"}, status_code=200)

    return JSONResponse(content={"results": response_data}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
