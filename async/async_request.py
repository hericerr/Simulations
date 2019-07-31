"""
Scrapes images from multiple Wikipedia pages asynchronously
"""
import asyncio
import logging
import sys

import aiofiles
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from timeit import async_timeit

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr)

logger = logging.getLogger('WikiCrawler')


async def fetch(url: str, session: ClientSession) -> str:
    """Asynchronous GET request
    
    :param url: url to fetch
    :param session: open aiohttp.ClientSession
    """
    resp = await session.request(method="GET", url=url)
    resp.raise_for_status()
    logger.info(f"Got response [{resp.status}] for URL: {url}")
    html = await resp.text()
    return html

async def parse(url: str, session: ClientSession) -> set:
    """Asynchronously parse the page and saves all images
    
    :param url: url to fetch
    :param session: open aiohttp.ClientSession
    """
    try:
        html = await fetch(url=url, session=session)
    except (
        aiohttp.ClientError,
        aiohttp.http_exceptions.HttpProcessingError,
    ) as e:
        logger.error(
            (f"aiohttp exception for {url} [{getattr(e, 'status', None)}]:"  
             f"{getattr(e, 'message', None)}")
            )
        logger.info(f"No images to write URL: {url}") 
    except Exception as e:
        logger.exception(
            f"Non-aiohttp exception occured: {getattr(e, '__dict__', {})}")
        logger.info(f"No images to write URL: {url}") 
    else:
        soup = BeautifulSoup(html, 'html.parser')
        image_soups = soup.findAll('img')
        logger.info(f"Found {len(image_soups)} images for {url}")
        for i, img_soup in enumerate(image_soups):
            if img_soup.get('src').startswith('/static'):
                continue
            try:
                async with session.get('https:'+img_soup.get('src')) as resp:
                    name = url.split('/')[-1] + f'_{img_soup.get("alt")}_{i}'
                    async with aiofiles.open(f'images/{name}.png', 'wb') as f:
                        await f.write(await resp.read())
            except Exception as e:
                logger.error(f'Error while parsing URL: {url}, message: {e}')
    logger.info(f"Wrote results for source URL: {url}")   

@async_timeit
async def main(urls: set) -> None:
    """Crawl and saves images from multiple wiki pages concurently
    
    :param urls: set of urls to crawl
    """
    async with ClientSession() as session:
        tasks = [parse(url=url, session=session) for url in urls]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('urls_file', help='file with urls to crawl')
    args = parser.parse_args()
    with open(args.urls_file) as f:
        urls = set(map(str.strip, f))
    asyncio.run(main(urls=urls))