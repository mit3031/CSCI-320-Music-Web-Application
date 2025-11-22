from .db import get_db
import pandas as pd
import random
from sklearn.metrics.pairwise import cosine_similarity
from flask import Blueprint, render_template, request, redirect, url_for, flash

# Song Reccomender based on cosine similarity matrix
# Author: Shuprovo Sikder
def recommend_songs(username: str) -> list:
    users = get_closest_users(username)

    similar_songs = set()
    for user in users:
        similar_songs = similar_songs.union(set(get_recent_songs(user[0])))

    sample = random.sample(list(similar_songs), 5)

    sql = """
        SELECT song_id, title 
        FROM song
        WHERE song_id = ANY(%s);
    """

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, (sample,))
        rows = cur.fetchall()
    
    return rows

def get_closest_users(username: str):
    art_sql = """
        SELECT username,
            artist_id,
            COUNT(artist_id) as art_count
        FROM listentosong AS lts
        JOIN makesong AS ms on lts.song_id = ms.song_id
        GROUP BY username, artist_id
        HAVING
            COUNT(artist_id) >= 1;
    """
    alb_sql = """
        SELECT username,
            album_id,
            COUNT(album_id) as alb_count
        FROM listentosong AS lts
        JOIN ispartofalbum AS ipalb ON lts.song_id = ipalb.song_id
        GROUP BY username, album_id
        HAVING
            COUNT(album_id) >= 1;
    """
    gen_sql = """
        SELECT username,
            genre_id,
            COUNT(genre_id) as gen_count
        FROM listentosong AS lts
        JOIN songhasgenre AS shg on lts.song_id = shg.song_id
        GROUP BY username, genre_id
        HAVING
            COUNT(genre_id) >= 1;
    """

    conn = get_db()

    df_art = pd.read_sql(art_sql, conn)
    art_matrix = df_art.pivot_table(index='username', columns='artist_id', values='art_count').fillna(0)
    art_similar = pd.DataFrame(cosine_similarity(art_matrix), index=art_matrix.index, columns=art_matrix.index)
    top_art = art_similar.loc[username].drop(username).sort_values(ascending=False).head(10)

    df_alb = pd.read_sql(alb_sql, conn)
    alb_matrix = df_alb.pivot_table(index='username', columns='album_id', values='alb_count').fillna(0)
    alb_similar = pd.DataFrame(cosine_similarity(alb_matrix), index=alb_matrix.index, columns=alb_matrix.index)
    top_alb = alb_similar.loc[username].drop(username).sort_values(ascending=False).head(10)

    df_gen = pd.read_sql(gen_sql, conn)
    gen_matrix = df_gen.pivot_table(index='username', columns='genre_id', values='gen_count').fillna(0)
    gen_similar = pd.DataFrame(cosine_similarity(gen_matrix), index=gen_matrix.index, columns=gen_matrix.index)
    top_gen = gen_similar.loc[username].drop(username).sort_values(ascending=False).head(10)

    top_users = {}
    for coll in [top_art, top_alb, top_gen]:
        for idx, val in coll.items():
            if idx not in top_users or val > top_users[idx]:
                top_users[idx] = val
    
    return sorted(top_users.items(), key=lambda x: x[1], reverse=True)[:5]

def get_recent_songs(username: str) -> list[int | None]:
    sql = """
        SELECT DISTINCT ON (song_id) song_id
        FROM listentosong
        WHERE username = %s
        ORDER BY song_id, datetime_listened DESC
        LIMIT 5;
    """

    conn = get_db()

    with conn.cursor() as cur:
        cur.execute(sql, (username,))
        rows = cur.fetchall()
    
    return [x[0] for x in rows]
