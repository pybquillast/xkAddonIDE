'''
Inspired by code of Esteban Ordano

http://estebanordano.com/ted-talks-download-subtitles/
http://estebanordano.com.ar/wp-content/uploads/2010/01/TEDTalkSubtitles.py_.zip
'''
import json
import urlparse
import urllib
import httplib
import re
# Custom xbmc thing for fast parsing. Can't rely on lxml being available as of 2012-03.
import CommonFunctions as xbmc_common  # @UnresolvedImport
import xbmc, xbmcgui, xbmcplugin  # @UnresolvedImport


def get(html, video_quality='320kbps'):
    """Extract talk details from talk html
       @param video_quality string in form '\d+kbps' that should match one of the provided TED bitrates.
    """
    init_scripts = [script for script in xbmc_common.parseDOM(html, 'script') if '"talkPage.init"' in script]
    if init_scripts:
        init_json = json.loads(re.compile(r'q[(]"talkPage.init",(.+)[)]').search(init_scripts[0]).group(1))
        talk_json = init_json['talks'][0]
        title = talk_json['title']
        speaker = talk_json['speaker']

        if talk_json['resources']['h264']:
            url = talk_json['resources']['h264'][0]['file']
            plot = xbmc_common.parseDOM(html, 'p', attrs={'class':'talk-description'})[0]

            if not video_quality == '320kbps':
                url_custom = url.replace("-320k.mp4", "-%sk.mp4" % (video_quality.split('k')[0]))

                # Test resource exists
                url_custom_parsed = urlparse.urlparse(url_custom)
                h = httplib.HTTPConnection(url_custom_parsed.netloc)
                h.request('HEAD', url_custom_parsed.path)
                response = h.getresponse()
                h.close()
                if response.status / 100 < 4:
                    url = url_custom
        else:
            # YouTube fallback
            youtube_code = talk_json['external']['code']
            url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % (youtube_code)
            plot = None  # Maybe it is there somewhere but this will do for now.

        return url, title, speaker, plot, talk_json

    else:
        # Vimeo fallback
        headline = xbmc_common.parseDOM(html, 'span', attrs={'id':'altHeadline'})[0].split(':', 1)
        # Note: maybe no ':' in title.
        title = headline[0].strip() if len(headline) == 1 else headline[1].strip()
        speaker = "Unknown" if len(headline) == 1 else headline[0].strip()
        plot = xbmc_common.parseDOM(html, 'p', attrs={'id':'tagline'})[0]

        vimeo_re = re.compile('https?://.*?vimeo.com/.*?/([^/?]+)')
        for link in xbmc_common.parseDOM(html, 'iframe', ret='src'):  # Can't get attrs regex to work properly with parseDOM :(
            match = vimeo_re.match(link)
            if match:
                url = 'plugin://plugin.video.vimeo?action=play_video&videoid=%s' % (match.group(1))
                break

        return url, title, speaker, plot, None


__friendly_message__ = 'Error showing subtitles'
__talkIdKey__ = 'id'
__introDurationKey__ = 'introDuration'

def format_time(time):
    millis = time % 1000
    seconds = (time / 1000) % 60
    minutes = (time / 60000) % 60
    hours = (time / 3600000)
    return '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, millis)

def format_subtitles(subtitles, introDuration):
    result = ''
    for idx, sub in enumerate(subtitles):
        start = introDuration + sub['start']
        end = start + sub['duration']
        result += '%d\n%s --> %s\n%s\n\n' % (idx + 1, format_time(start), format_time(end), sub['content'])
    return result

def __get_languages__(talk_json):
    '''
    Get languages for a talk, or empty array if we fail.
    '''
    return [l['languageCode'] for l in talk_json['languages']]

# def get_subtitles(talk_id, language, logger):
def get_subtitles(talk_id, language):
    url = 'http://www.ted.com/talks/subtitles/id/%s/lang/%s' % (talk_id, language)
    subs = json.loads(urllib.urlopen(url).read())
    captions = []
    for caption in subs['captions']:
        captions += [{'start': caption['startTime'], 'duration': caption['duration'], 'content': caption['content']}]
    return captions

# def get_subtitles_for_talk(talk_json, accepted_languages, logger):
def get_subtitles_for_talk(talk_json, accepted_languages):
    '''
    Return subtitles in srt format, or notify the user and return None if there was a problem.
    '''
    talk_id = talk_json['id']
    intro_duration = talk_json['introDuration']

    try:
        languages = __get_languages__(talk_json)

        if len(languages) == 0:
            msg = 'No subtitles found'
#             logger(msg, msg)
            return None

        language_matches = [l for l in accepted_languages if l in languages]
        if not language_matches:
            msg = 'No subtitles in: %s' % (",".join(accepted_languages))
#             logger(msg, msg)
            return None

#         raw_subtitles = get_subtitles(talk_id, language_matches[0], logger)
        raw_subtitles = get_subtitles(talk_id, language_matches[0])
        if not raw_subtitles:
            return None

        return format_subtitles(raw_subtitles, int(float(intro_duration) * 1000))

    except Exception, e:
        # Must not fail!
#         logger('Could not display subtitles: %s' % (e), __friendly_message__)
        return None
