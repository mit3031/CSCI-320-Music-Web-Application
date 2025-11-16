from ..db import get_db

# Set of SQL queries and calls on getting data for song reccomender
# Author: Sean Allen

# ----- Get User Histroy ---------------------------------------------------------------
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

# ----- Get all album IDs ---------------------------------------------------------------
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