from app.dao.database_reccomender import get_album_ids, get_song_id_history, song_in_album

# ----- Get top 3 most listened to albums all time
def get_top_3_all_time(username: str):
    album_dict = dict()

    song_ids = get_song_id_history(username)
    album_ids = get_album_ids()

    #Adds songs to album
    for album in album_ids:
        for song in song_ids:
            if(song_in_album(song)):
                if album not in album_dict:
                    album_dict[album] = []
                album_dict[album].append(song)

    #get list of top 3 albums
    top_3 = [0] * 3
    for i in range(3):
        largest_album, dictionary = get_largest_album(album_dict)
        top_3[i] = largest_album
        album_dict = dictionary

    return top_3

def get_largest_album(dictionary: dict) -> tuple[int, dict]:
    largest_key = max(dictionary)
    dictionary.pop(largest_key)
    return largest_key, dictionary




