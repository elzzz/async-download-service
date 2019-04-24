import asyncio
import argparse
import os
from aiohttp import web
import aiofiles
import logging
from functools import partial


async def archivate(request, photos_dir_path='/photos', download_speed_limit=False, **kwargs):
    archive_hash = request.match_info['archive_hash']
    archivate_path = f'{photos_dir_path}/{archive_hash}'

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
        web.get('/archive/{archive_hash}/', partial(archivate, **kwargs)),
    ])
    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AioHttp server with photos hosting')
    parser.add_argument('-v', '--verbose', type=int, choices=[0, 10, 20, 30, 40, 50], default=0,
                        help='Increase output verbosity.')
    parser.add_argument('-d', '--download-speed-limit', action='store_true', help='Add download limit speed.')
    parser.add_argument('-p', '--photos-dir-path', help='Custom path to files to archive.')
    kwargs = {k: v for k, v in vars(parser.parse_args()).items() if v is not None}

    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=kwargs['verbose'])

    app = init_app()
    web.run_app(app)
