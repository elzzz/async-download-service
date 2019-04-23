import asyncio
import argparse
import os
from aiohttp import web
import aiofiles
import logging
from functools import partial

INTERVAL_SECS = 1


async def archivate(request, photos_dir_path=None, download_speed_limit=False):
    archive_hash = request.match_info['archive_hash']

    if photos_dir_path:
        archivate_path = f'{photos_dir_path}/{archive_hash}'
    else:
        archivate_path = f'/photos/{archive_hash}'

    if not os.path.exists(archivate_path):
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
            if download_speed_limit:
                await asyncio.sleep(1)
            logging.info('Sending archive chunk ...')
    except asyncio.CancelledError:
        logging.info('User stopped archive downloading')
        archive_chunk.terminate()
        raise
    finally:
        logging.info('Terminating archive chunk')
        response.force_close()

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


def init_app():
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', partial(archivate, photos_dir_path=args.photos_dir_path,
                                                    download_speed_limit=args.download_speed_limit)),
    ])
    return app


def main():
    if args.logs:
        logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                            level=logging.INFO)

    app = init_app()
    web.run_app(app)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AioHttp server with photos hosting')
    parser.add_argument('--logs', action='store_true')
    parser.add_argument('--download-speed-limit', action='store_true')
    parser.add_argument('--photos-dir-path')
    args = parser.parse_args()
    main()
