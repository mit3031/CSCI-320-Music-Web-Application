from ..db import get_db

# Set of SQL queries and calls on getting data for song reccomender
# Author: Sean Allen

# ----- Get User Histroy 
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