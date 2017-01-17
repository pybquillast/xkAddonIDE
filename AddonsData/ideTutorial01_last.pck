["channelraw", {"kodivideos": {"name": "kodivideos", "numid": 5, "up": "media", "down": "kodi_kodivideos_lnk", "sibling": "channelvideos", "params": {"url": "https://www.youtube.com/results?q=kodi", "regexp": "(?#<ol class=\"item-section\" .li< .h3.a{href=url *=label} .img.src=iconImage>*>)", "nextregexp": "Next>>><->|(?#<a class=\"yt-uix-button\\s+vve-check[^\"]+\" href=url span.*=\"Next.+?\">)"}, "type": "thread"}, "kodivideos_kodi_lnk": {"name": "kodivideos", "numid": 7, "up": "kodi", "sibling": "kodichannels_kodi_lnk", "params": {"source": true}, "type": "link"}, "channelitems": {"name": "channelitems", "numid": 12, "up": "channelvideos", "down": "kodichannels", "sibling": "playlistvideos_channelvideos_lnk", "params": {"url": "https://www.youtube.com/channel/UCWJ3sjHCtaO240IYKueqkNw", "regexp": "(?#<h2 class=\"branded-[^\"]+\" .a{href=url span.span.*=label}>)"}, "type": "thread"}, "playlists": {"name": "playlists", "numid": 16, "up": "playlistraw", "down": "kodi_playlists_lnk", "params": {"url": "https://www.youtube.com/results?q=kodi&sp=EgIQAw%253D%253D", "regexp": "(?#<ol class=\"item-section\" .li< .ul.li.a.*=\".+?(\\([^)]+\\))\"=label3 .h3.a{href=\"/watch[^\"]+\"=url *=label} .img{src=iconImage data-thumb=_iconImage_}>*>)", "nextregexp": "Next>>><->|(?#<a class=\"yt-uix-button\\s+vve-check[^\"]+\" href=url span.*=\"Next.+?\">)"}, "type": "thread"}, "kodi": {"name": "kodi", "numid": 3, "up": "rootmenu", "down": "kodivideos_kodi_lnk", "sibling": "python", "params": {"discrim": "option"}, "type": "list"}, "python": {"params": {}, "numid": 4, "type": "list", "name": "python", "up": "rootmenu"}, "media": {"down": "kodivideos", "type": "thread", "numid": 2, "params": {"url": "https://www.youtube.com/watch?v=aCWRPqLt0wE", "regexp": "\"adaptive_fmts\":\"(?P<youtube_fmts>[^\"]+)\"", "compflags": "re.DOTALL"}, "name": "media"}, "kodichannels_kodi_lnk": {"name": "kodichannels", "numid": 11, "up": "kodi", "sibling": "playlists_kodi_lnk", "params": {"source": true}, "type": "link"}, "rootmenu": {"down": "kodi", "type": "list", "numid": 1, "params": {}, "name": "rootmenu"}, "channelvideos_playlistvideos_lnk": {"type": "link", "numid": 14, "params": {}, "name": "channelvideos", "up": "playlistvideos"}, "kodichannels": {"name": "kodichannels", "numid": 8, "up": "channelitems", "down": "kodi_kodichannels_lnk", "params": {"url": "https://www.youtube.com/results?sp=EgIQAg%253D%253D&q=kodi", "regexp": "(?#<ol class=\"item-section\" .li< .h3.a{href=url *=label} .img.src=iconImage>*>)", "nextregexp": "Next>>><->|(?#<a class=\"yt-uix-button\\s+vve-check[^\"]+\" href=url span.*=\"Next.+?\">)"}, "type": "thread"}, "playlistvideos": {"name": "playlistvideos", "numid": 13, "up": "media", "down": "channelvideos_playlistvideos_lnk", "sibling": "playlistraw", "params": {"url": "https://www.youtube.com/playlist?list=PLh7f1OBeq3lIZtDOWjIhIrz4HoepRtvC4", "regexp": "(?#<tr  .td[4].a{href=url *=&label&} .img.data-thumb=iconImage>)", "urlout": "/playlist"}, "type": "thread"}, "kodi_playlists_lnk": {"params": {}, "numid": 18, "type": "link", "name": "kodi", "up": "playlists"}, "channelvideos": {"name": "channelvideos", "numid": 9, "up": "media", "down": "channelitems", "sibling": "playlistvideos", "params": {"url": "https://www.youtube.com/user/teamxbmc", "regexp": "(?#<li class=\"channels-[^\"]+-item ?\" .h3.a{href=url *=label} .img.src=iconImage>)", "discrim": "urlout"}, "type": "thread"}, "playlistraw": {"name": "playlistraw", "numid": 17, "up": "media", "down": "playlists", "sibling": "channelraw", "params": {"url": "https://www.youtube.com/watch?v=Cz3WauQ5BBI&amp;list=PLR4czbB8dznzD6Mu28LoPFu4p0URXEg_U", "regexp": "(?#<ol .li< data-video-title=label a.href=url .img{src=iconImage data-thumb=_iconImage_}>*>)"}, "type": "thread"}, "kodi_kodichannels_lnk": {"type": "link", "numid": 10, "params": {}, "name": "kodi", "up": "kodichannels"}, "kodi_kodivideos_lnk": {"type": "link", "numid": 6, "params": {}, "name": "kodi", "up": "kodivideos"}, "channelraw": {"params": {"url": "https://www.youtube.com/channel/UCk17yyK15sTiTMrhoBgus9g", "regexp": "(?#<div class=\"feed-item-main\" .h3.a{*=label href=url} .img{src=iconImage data-thumb=_iconImage_}>)"}, "numid": 20, "type": "thread", "name": "channelraw", "up": "media"}, "playlists_kodi_lnk": {"params": {"source": true}, "numid": 19, "type": "link", "name": "playlists", "up": "kodi"}, "playlistvideos_channelvideos_lnk": {"type": "link", "numid": 15, "params": {"source": true}, "name": "playlistvideos", "up": "channelvideos"}}]
{"addon_id": "plugin.video.idetutorial01", "addon_requires": "xbmc.python,2.1.0,|script.module.urlresolver,2.4.0,", "addon_name": "Addon IDE Tutorial01"}
[]
