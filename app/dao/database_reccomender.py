from ..db import get_db

# Set of SQL queries and calls on getting data for song reccomender
# Author: Sean Allen

# ----- Get All User Song Histroy 
def get_song_ids():
    sql = """
        SELECT song_id
        FROM song
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [row[0] for row in rows]

# ----- Get All User Song Histroy 
def get_song_id_history(username: str):
    sql = """
        SELECT song_id
        FROM listentosong
        WHERE username = %s;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (username,))
        rows = cur.fetchall()
    return [row[0] for row in rows]

# ----- Get all album IDs 
def get_album_ids():
    sql = """
        SELECT album_id
        FROM album;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [row[0] for row in rows]

# ----- Checks to see if song is in album 
def song_in_album(song_id: int, album_id: int) -> bool:
    sql = """
        SELECT 1
        FROM ispartofalbum
        WHERE song_id = %s AND album_id = %s
        LIMIT 1;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (song_id, album_id))
        row = cur.fetchone()

    return row is not None

# ----- Get all genres IDs 
def get_genres_ids():
    sql = """
        SELECT genre_id
        FROM genre;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [row[0] for row in rows]

# ----- Checks to see if song is in genre
def song_in_genre(song_id: int, genre_id: int) -> bool:
    sql = """
        SELECT 1
        FROM songhasgenre
        WHERE song_id = %s AND genre_id = %s
        LIMIT 1;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (song_id, genre_id))
        row = cur.fetchone()

    return row is not None

# ----- Get all artist IDs 
def get_artist_ids():
    sql = """
        SELECT artist_id
        FROM artist;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [row[0] for row in rows]

# ----- Checks to see if song associated with artist
def song_with_artist(song_id: int, artist_id: int) -> bool:
    sql = """
        SELECT 1
        FROM makesong
        WHERE song_id = %s AND artist_id = %s
        LIMIT 1;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (song_id, artist_id))
        row = cur.fetchone()

    return row is not None

# ----- Get User Song Histroy for day function is called
def get_song_id_history(username: str):
    sql = """
        SELECT song_id
        FROM listentosong
        WHERE username = %s
          AND DATE(datetime_listened) = CURRENT_DATE;
    """
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (username,))
        rows = cur.fetchall()
    return [row[0] for row in rows]