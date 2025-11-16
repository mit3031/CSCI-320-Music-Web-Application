from app.dao.database_reccomender import get_album_ids, get_artist_ids, get_genres_ids, get_song_id_history_recent, get_song_ids, get_usernames, song_in_album, song_in_genre, song_with_artist, get_song_id_history_all_time

#Author: Sean Allen

def get_largest_key(dictionary: dict) -> tuple[int, dict]:
    largest_key = max(dictionary)
    dictionary.pop(largest_key)
    return largest_key, dictionary

# ----- Get top 3 most listened to albums
def get_top_3_album(username: str, song_list: list):
    album_dict = dict()

    song_ids = song_list
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

# ----- Get top 3 most listened to genre
def get_top_3_genre(username: str, song_list: list):
    genre_dict = dict()

    song_ids = song_list
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

# ----- Get top 3 most listened to artist
def get_top_3_artist(username: str, song_list: list):
    artist_dict = dict()

    song_ids = song_list
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

def get_top_3_all_time(username: str):
    song_list = get_song_id_history_all_time(username)

    album_3 = get_top_3_album(username, song_list)
    genre_3 = get_top_3_genre(username, song_list)
    artist_3 = get_top_3_artist(username, song_list)

    return album_3, genre_3, artist_3

def get_top_3_recent(username: str):
    song_list = get_song_id_history_recent(username)

    album_3 = get_top_3_album(username, song_list)
    genre_3 = get_top_3_genre(username, song_list)
    artist_3 = get_top_3_artist(username, song_list)

    return album_3, genre_3, artist_3


# -----Similarity Matrix, Feature Vector, Cosine Similatrity

## -----Makes Indexes in a vector accesible 
##(amount of values a the program has to work inside a user)
def get_vector_length():
    ALL_SONG_IDS = get_song_ids()
    #enumerate: 
    SONG_INDEX = {song_id: i for i, song_id in enumerate(ALL_SONG_IDS)}
    return len(ALL_SONG_IDS), SONG_INDEX

# -----Createing a vector for each song, all time
def build_user_vector_all_time(username: str) -> list[float]:
    history = get_song_id_history_all_time(username)
    vector_length, song_index =  get_vector_length()
    vec = [0.0] * vector_length #defines length of array

    #get weights, Categorical Attributes so make scores be more accurate based on additional factors


    #for each song give the inde x a score of 1
    for song_id in history:
        idx = song_index.get(song_id)
        if idx is not None:
            vec[idx] += 1.0
    return vec

## -----Createing a vector for each song, recent
def build_user_vector_recent(username: str):
    history = get_song_id_history_recent(username)
    vector_length, song_index =  get_vector_length()

    #if no songs return 0 for all indexes
    if not history:
        return False, [0.0] * vector_length
    vec = [0.0] * vector_length

    #for each song give the inde x a score of 1
    for song_id in history:
        idx = song_index.get(song_id)
        if idx is not None:
            vec[idx] += 1.0
    return True, vec

### ----- Cosine Similarity Calcuation Functions
### cos(0) = (A*B)/(||A|||B||)
### (A*B) = Dot Product, sum of results from multiplying vectors together
### ||A|| and ||BB| are the magnitude (or absolute values)
### All return a score of 0 - 1, 1 being the most similar

def dot_product(vec1, vec2):
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same length")
    return sum(v1 * v2 for v1, v2 in zip(vec1, vec2))

def magnitude(vec):
    return sum(v**2 for v in vec)**0.5

def cosine_similarity(vec1, vec2):
    dp = dot_product(vec1, vec2)
    mag1 = magnitude(vec1)
    mag2 = magnitude(vec2)

    if mag1 == 0 or mag2 == 0:
        return 0.0  # Handle zero vectors
    return dp / (mag1 * mag2)

def cosine_similarity_matrix(vectors):
    num_vectors = len(vectors)
    # Initialize a square matrix with zeros
    similarity_matrix = [[0.0 for _ in range(num_vectors)] for _ in range(num_vectors)]

    ##Assing scores to each index in the vector
    for i in range(num_vectors):
        for j in range(num_vectors):
            if i == j:
                similarity_matrix[i][j] = 1.0
            else:
                similarity_matrix[i][j] = cosine_similarity(vectors[i], vectors[j])
    return similarity_matrix

def get_closest_user_recent(target_username):
    users = get_usernames()

    #track if target has recent activity
    has_recent_target, target_vec = build_user_vector_recent(target_username)
    if not has_recent_target:
        return False, None

    #build vectors
    vectors: dict[str, list[float]] = {}
    for u in users:
        if u == target_username:
            continue
        has_recent, vec = build_user_vector_recent(u)
        if has_recent:
            vectors[u] = vec

    if not vectors:
        return False, None

    best_user = None
    best_score = -1.0

    #set scores
    for u, vec in vectors.items():
        score = cosine_similarity(target_vec, vec)
        if score > best_score:
            best_score = score
            best_user = u

    return True, best_user

def get_closest_user_all_time(target_username: str):
    users = get_usernames()

    # build vectors for everyone
    vectors: dict[str, list[float]] = {}
    for u in users:
        vectors[u] = build_user_vector_all_time(u)

    target_vec = vectors[target_username]

    best_user = None
    best_score = -1.0

    #set scores
    for u, vec in vectors.items():
        if u == target_username:
            continue
        score = cosine_similarity(target_vec, vec)
        if score > best_score:
            best_score = score
            best_user = u

    return best_user