from app.dao.database_reccomender import get_album_ids, get_artist_ids, get_genres_ids, get_song_id_history, song_in_album, song_in_genre, song_with_artist

#Author: Sean Allen

def get_largest_key(dictionary: dict) -> tuple[int, dict]:
    largest_key = max(dictionary)
    dictionary.pop(largest_key)
    return largest_key, dictionary

# ----- Get top 3 most listened to albums all time
def get_top_3_album_all_time(username: str):
    album_dict = dict()

    #rember to remove and pass in parameter in later for this so you don't forget it
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
        largest_album, dictionary = get_largest_key(album_dict)
        top_3[i] = largest_album
        album_dict = dictionary

    return top_3

# ----- Get top 3 most listened to genres all time
def get_top_3_genre_all_time(username: str):
    genre_dict = dict()

    #REMEBER to remove and pass in parameter in later for this so you don't forget it
    song_ids = get_song_id_history(username)
    genre_ids = get_genres_ids()

    #Adds songs to album
    for genre in genre_ids:
        for song in song_ids:
            if(song_in_genre(song, genre)):
                if genre not in genre_dict:
                    genre_dict[genre] = []
                genre_dict[genre].append(song)

    #get list of top 3 albums
    top_3 = [0] * 3
    for i in range(3):
        largest_genre, dictionary = get_largest_key(genre_dict)
        top_3[i] = largest_genre
        genre_dict = dictionary

    return top_3

def get_top_3_artist_all_time(username: str):
    artist_dict = dict()

    #REMEBER to remove and pass in parameter in later for this so you don't forget it
    song_ids = get_song_id_history(username)
    artist_ids = get_artist_ids()

    #Adds songs to album
    for artist in artist_ids:
        for song in song_ids:
            if(song_with_artist(song, artist)):
                if artist not in artist_dict:
                    artist_dict[artist] = []
                artist_dict[artist].append(song)

    #get list of top 3 albums
    top_3 = [0] * 3
    for i in range(3):
        largest_artist, dictionary = get_largest_key(artist_dict)
        top_3[i] = largest_artist
        artist_dict = dictionary

    return top_3



