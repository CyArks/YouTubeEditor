from pprint import pprint
import YouTubeEditor as YTE

playlistIds = []


for playlistId in playlistIds:
    p = YTE.Playlist(PlaylistID=playlistId)
    p.createBackup()

se = YTE.Search().search("One Republic")
pprint(se)

# Pl = Playlist()
# pprint(Pl.listMine())
# pprint(Pl.listMyLikes())

# x = Pl.create("TestPlaylist", "private")
# print(x)
