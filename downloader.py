__author__ = 'Artur Karwowski'
from urllib import parse, request, error
from functools import wraps
import re
import threading
import sys


class Video(object):
    def __init__(self, video_id, raw_string):
        self.video_id = video_id
        self.raw_string = raw_string
        self.url = self.__extract_url()
        self.codec = self.__extract_codec()

    def __extract_url(self):
        return self.raw_string.split("url=", 1)[1]

    def __extract_codec(self):
        return re.search(".*codecs=\"(.*)\".*", self.raw_string).group(1)


class VideoInfoParser(object):
    GET_VIDEO_INFO_URL = "http://www.youtube.com/get_video_info?video_id="
    DEFAULT_ENCODING = "utf-8"

    def get_videos(self, video_id):
        response = request.urlopen(VideoInfoParser.GET_VIDEO_INFO_URL + video_id).read().decode(
            VideoInfoParser.DEFAULT_ENCODING)

        # response is double urlencoded
        decoded_response = parse.unquote_plus(parse.unquote_plus(response))
        split_response_list = decoded_response.split(';')

        return [Video(video_id, splitted_item) for splitted_item in split_response_list[1:]]


def async(function):
    @wraps(function)
    def run_asynchronously(*args, **kwargs):
        thread = threading.Thread(target=function, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return run_asynchronously


class VideoDownloader(object):
    @async
    def download_video(self, video):
        try:
            request.urlretrieve(video.url, video.video_id + "-" + video.codec)
        except error.HTTPError as e:
            print(str(e.code) + " response , video with codec: " + video.codec)


def main():
    assert len(sys.argv) == 2, "usage: $ python downloader.py <video_id parameter from youtube link>"
    video_id = sys.argv[1]
    video_info_parser = VideoInfoParser()
    video_downloader = VideoDownloader()

    for video in video_info_parser.get_videos(video_id):
        video_downloader.download_video(video)


if __name__ == '__main__':
    main()

