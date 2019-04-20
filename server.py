import asyncio
import argparse
import os
from aiohttp import web
import aiofiles
import logging

INTERVAL_SECS = 1

parser = argparse.ArgumentParser(description='AioHttp server with photos hosting')
parser.add_argument('--logs', action='store_true')
parser.add_argument('--download-limit-speed', action='store_true')
parser.add_argument('--photos-path')


async def archivate(request):
    archive_hash = request.match_info['archive_hash']

    if PHOTOS_PATH:
        archivate_path = f'{PHOTOS_PATH}/{archive_hash}'
    else:
        archivate_path = f'test_photos/{archive_hash}'

        logging.info(archivate_path)
        logging.info(os.getcwd())

    if not os.path.exists(archivate_path):
        if LOGS:
            logging.error('Archive does not exist')
        raise web.HTTPNotFound(text='Archive does not exist.')

    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'attachment; filename="archive.zip"'
    await response.prepare(request)

    archive_chunk = await asyncio.create_subprocess_shell(
        f'zip -jr - {archivate_path}',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    try:
        while True:
            line = await archive_chunk.stdout.readline()
            if not line:
                break
            await response.write(line)
            if DOWNLOAD_LIMIT_SPEED:
                await asyncio.sleep(1)
            if LOGS:
                logging.info('Sending archive chunk ...')
    except asyncio.CancelledError:
        if LOGS:
            logging.info('User stopped archive downloading')
        archive_chunk.terminate()
        raise
    finally:
        if LOGS:
            logging.info('Terminating archive chunk')

        response.force_close()

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    args = parser.parse_args()
    global LOGS, PHOTOS_PATH, DOWNLOAD_LIMIT_SPEED
    LOGS = args.logs
    PHOTOS_PATH = args.photos_path
    DOWNLOAD_LIMIT_SPEED = args.download_limit_speed

    # if LOGS:
    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO)

    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app)

