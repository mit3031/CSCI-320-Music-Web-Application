#
# Implements popularity lists for songs and artists
# Author: Joseph Britton (jtb8595)
#

import psycopg

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from .db import get_db
import datetime

bp = Blueprint("popular", __name__, url_prefix="/popular")

# SEARCH FUNCTIONS

#
# Retrives the top 50 songs of the past 30 days
# As well as any data necessary to display them
# Author: Joseph Britton (jtb8595)
#
@bp.route("/songs", methods=["GET", "POST"])
@login_required
def songs_popular():
    if request.method == "POST":

        db_conn = get_db()
        try:
            with db_conn.cursor() as curs:
                query = perform_select_query(curs, 
                    'SELECT DISTINCT so.song_id, so.title, ar.name, al.name, g.name AS genre, ' \
                    'so.length, so.release_date, popular.times_listened ' \
                    'FROM ' \
                    '   (SELECT song_id, COUNT(datetime_listened) AS times_listened ' \
                    '   FROM listentosong ' \
                    '   WHERE datetime_listened > NOW() - INTERVAL \'30 day\' ' \
                    '   GROUP BY song_id ' \
                    '   ORDER BY times_listened DESC ' \
                    '   LIMIT 50) AS popular ' \
                    'INNER JOIN song AS so ON (so.song_id = popular.song_id) ' \
                    'INNER JOIN makesong AS m ON (m.song_id = so.song_id) ' \
                    'INNER JOIN artist AS ar ON (ar.artist_id = m.artist_id) ' \
                    'INNER JOIN ispartofalbum AS i ON (i.song_id = so.song_id) ' \
                    'INNER JOIN album AS al ON (al.album_id = i.album_id) ' \
                    'INNER JOIN songhasgenre AS h ON (h.song_id = so.song_id) ' \
                    'INNER JOIN genre AS g on (g.genre_id = h.genre_id) ' \
                    'ORDER BY popular.times_listened DESC'
                )
                #
                # curs.fetchall[x] = [song id, song title, artist, album, genre, length, 
                # release date, how many listens in the past 30 days]
                #
                results = format_song_query_results(query)

                # Warning for debug: <50 is possible, >50 should not be.
                if (len(results) > 50):
                    print(f"There's {len(results)} entries in results, " +
                        "which is supposed to be a top 50. Just a heads up." )
                
                db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            flash(f"Database error: {e}")
            return f"Database error: {e}", 500
        
        
        return render_template("popular/songs.html", results=results)
    
    return render_template("popular/popular.html")


#
# Retrives the top 50 songs among the current user's followers
# As well as any data necessary to display them
# Author: Joseph Britton (jtb8595)
#
@bp.route("/followed", methods=["GET", "POST"])
@login_required
def followed_popular():
    if request.method == "POST":
        user = current_user.id

        db_conn = get_db()
        try:
            with db_conn.cursor() as curs:
                query = perform_select_query(curs, 
                    'SELECT DISTINCT song.song_id, song.title, ar.name, al.name, g.name AS genre, ' \
                    'song.length, song.release_date, popular.times_listened ' \
                    'FROM ' \
                    '   (SELECT so.song_id, COUNT(l.datetime_listened) AS times_listened ' \
                    '   FROM "song" as so ' \
                    '   INNER JOIN ' \
                    '       (SELECT song_id, datetime_listened ' \
                    '       FROM "listentosong" AS lts ' \
                    '       WHERE lts.username IN ' \
                    '           (SELECT followed_username ' \
                    '           FROM "followuser" ' \
                    f'          WHERE follow_username = \'{user}\'))' \
                    '   AS l ON (so.song_id = l.song_id) ' \
                    '   GROUP BY so.song_id ' \
                    '   ORDER BY times_listened DESC ' \
                    '   LIMIT 50) ' \
                    'AS popular ' \
                    'INNER JOIN song ON (popular.song_id = song.song_id) ' \
                    'INNER JOIN makesong AS m ON (m.song_id = song.song_id) ' \
                    'INNER JOIN artist AS ar ON (ar.artist_id = m.artist_id) ' \
                    'INNER JOIN ispartofalbum AS i ON (i.song_id = song.song_id) ' \
                    'INNER JOIN album AS al ON (al.album_id = i.album_id) ' \
                    'INNER JOIN songhasgenre AS shg ON (shg.song_id = song.song_id) ' \
                    'INNER JOIN genre AS g ON (g.genre_id = shg.genre_id) ' \
                    'ORDER BY popular.times_listened DESC'
                )
                #
                # curs.fetchall[x] = [song id, song title, artist, album, genre, length, 
                # release date, how many listens among followed users]
                #
                results = format_song_query_results(query)

                # Warning for debug: <50 is possible, >50 should not be.
                if (len(results) > 50):
                    print(f"There's {len(results)} entries in results, " +
                        "which is supposed to be a top 50. Just a heads up." )
                
                db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            flash(f"Database error: {e}")
            return f"Database error: {e}", 500
        
        
        return render_template("popular/songs.html", results=results)
    
    return render_template("popular/popular.html")

#
# Retrives the top 5 genres of the month
# Author: Joseph Britton (jtb8595)
#
@bp.route("/genre", methods=["GET", "POST"])
@login_required
def popular_genres():
    if request.method == "POST":
        db_conn = get_db()
        try:
            with db_conn.cursor() as curs:
                popular = perform_select_query(curs, 
                    'SELECT g.genre_id, g.name, popular.count ' \
                    'FROM ' \
                    '   (SELECT g.genre_id, COUNT(l.datetime_listened) AS count ' \
                    '   FROM listentosong AS l ' \
                    '   INNER JOIN songhasgenre AS h ON (h.song_id = l.song_id) ' \
                    '   INNER JOIN genre AS g ON (g.genre_id = h.genre_id) ' \
                    '   WHERE EXTRACT(YEAR FROM l.datetime_listened) = EXTRACT(YEAR FROM CURRENT_DATE) ' \
                    '   AND EXTRACT(MONTH FROM l.datetime_listened) = EXTRACT(MONTH FROM CURRENT_DATE) ' \
                    '   GROUP BY g.genre_id ' \
                    '   ORDER BY count DESC ' \
                    '   LIMIT 5) AS popular ' \
                    'INNER JOIN genre AS g ON (g.genre_id = popular.genre_id) ' \
                    'ORDER BY popular.count DESC' \
                )

                results = [] 

                # Construct the results
                for entry in popular:
                    results.append({
                        "genre_id": entry[0],
                        "name": entry[1],
                        "times_listened": entry[2]
                    })

                # Warning for debug: <5 is possible, >5 should not be.
                if (len(results) > 5):
                    print(f"There's {len(results)} entries in results, " +
                        "which is supposed to be a top 5. Just a heads up." )
                
                db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            flash(f"Database error: {e}")
            return f"Database error: {e}", 500
        
        
        return render_template("popular/genres.html", results=results)
    
    return render_template("popular/popular.html")


# FUNCTIONS LIFTED/ADAPTED FROM OTHER FILES

#
# Searches the database for songs that have a given genre
# Based on the search_by="genre" branch of song_search from song_search.py
# Author: Joseph Britton (jtb8595)
#
@bp.route("/search_by_genre", methods=["GET", "POST"])
@login_required
def search_songs_by_genre():
    if request.method == "POST":
        search_term = request.form["search"].strip()  # Whatever's in the search bar

        db_conn = get_db()
        try:
            with db_conn.cursor() as curs:
                songs = perform_select_query(curs, 
                    'SELECT DISTINCT so.song_id, so.title, ar.name, al.name, g.name AS genre, so.length, so.release_date '
                    'FROM "genre" AS g '
                    'INNER JOIN "songhasgenre" AS h ON (h.genre_id = g.genre_id) '
                    'INNER JOIN "song" AS so ON (so.song_id = h.song_id) '
                    'INNER JOIN "makesong" AS m ON (so.song_id = m.song_id) '
                    'INNER JOIN "artist" AS ar ON (ar.artist_id = m.artist_id) '
                    'INNER JOIN "ispartofalbum" AS i ON (so.song_id = i.song_id) '
                    'INNER JOIN "album" AS al ON (i.album_id = al.album_id) '
                    f'WHERE g.name LIKE \'%%{search_term}%%\' '
                    'ORDER BY so.title ASC, ar.name ASC'
                )

                # songs[x] = [song id, song name, artist, album, genre, song length, release_date]

                song_ids = []
                results = []  # [name, artist, album, length, number of times listened]

                # Organize search results
                for song in songs:
                    # check if the song is not already in results
                    if song[0] not in song_ids:
                        # Not in results - add it

                        # Get times listened to song
                        curs.execute(
                            'SELECT COUNT(*) '
                            'FROM "listentosong" '
                            f'WHERE song_id = {song[0]}',
                            []
                        )

                        # Add song information to results
                        results.append({
                            "song_id": song[0],
                            "name": song[1], 
                            "artist": song[2], 
                            "album": song[3], 
                            "genre": song[4],
                            "length": song[5],
                            "release_date": song[6],
                            "listened": curs.fetchone()[0]
                        })
                        song_ids.append(song[0])
                    else:
                        toCheck = results[song_ids.index(song[0])]
                        # In results - add the artist to song information if not already there
                        if song[2] not in toCheck['artist']:
                            results[song_ids.index(song[0])]['artist'] += ", " + song[2]
                        # Do the same for album
                        if song[3] not in toCheck['album']:
                            results[song_ids.index(song[0])]['album'] += ", " + song[3]
                        # Do the same for genre
                        if song[4] and song[4] not in toCheck['genre']:
                            results[song_ids.index(song[0])]['genre'] += ", " + song[4]

                db_conn.commit()
        except psycopg.Error as e:
            db_conn.rollback()
            flash(f"Database error: {e}")
            return f"Database error: {e}", 500
    
        return render_template("popular/search_by_genre.html", results=results, search_term=search_term)
    
    return render_template("popular/genres.html")
#
# Handles sorting the results of a search by genre
# Adapted from the genre branch of sort_songs from song_search.py
# Did not write that one, and I didn't modify the branch
# Author: Joseph Britton (jtb8595)
#
@bp.route("/sort_songs", methods=["POST"])
@login_required
def sort_songs():
    sort_by = request.form.get("sort_by")
    direction = request.form.get("direction", "asc")
    search_term = request.form.get("search_term")

    db_conn = get_db()
    results = []

    sort_map = {
        "song_name": "so.title",
        "artist": "artist_names",
        "genre": "genre_names",
        "year": "so.release_date"
    }
    order_col = sort_map.get(sort_by, "so.title")
    order_dir = "ASC" if direction == "asc" else "DESC"

    
    
    

    try:
        with db_conn.cursor() as curs:
            query = f'''
                SELECT
                    so.song_id,
                    so.title,
                    STRING_AGG(DISTINCT ar.name, ', ') AS artist_names,
                    STRING_AGG(DISTINCT al.name, ', ') AS album_names,
                    STRING_AGG(DISTINCT g.name, ', ') AS genre_names,
                    so.length,
                    so.release_date
                FROM "song" AS so
                INNER JOIN "makesong" AS m ON so.song_id = m.song_id
                INNER JOIN "artist" AS ar ON ar.artist_id = m.artist_id
                INNER JOIN "ispartofalbum" AS i ON so.song_id = i.song_id
                INNER JOIN "album" AS al ON al.album_id = i.album_id
                LEFT JOIN "songhasgenre" AS h ON so.song_id = h.song_id
                LEFT JOIN "genre" AS g ON g.genre_id = h.genre_id
                WHERE g.name ILIKE %s
                GROUP BY so.song_id, so.title, so.length, so.release_date
                ORDER BY {order_col} {order_dir}
            '''
            curs.execute(query, [f"%{search_term}%"])
            songs = curs.fetchall()

            for song in songs:
                curs.execute(
                    'SELECT COUNT(*) FROM "listentosong" WHERE username = %s AND song_id = %s',
                    [current_user.id, song[0]]
                )
                listens = curs.fetchone()[0]

                results.append({
                    "song_id": song[0],
                    "name": song[1],
                    "artist": song[2],
                    "album": song[3],
                    "genre": song[4] if song[4] else "—",
                    "length": song[5],
                    "release_date": song[6],
                    "listened": listens
                })

        db_conn.commit()

    except psycopg.Error as e:
        db_conn.rollback()
        flash(f"Database error: {e}")
        return f"Database error: {e}", 500

    return render_template("popular/search_by_genre.html", results=results, search_term=search_term)

#
# Handles song playback in popular lists for songs
# Directly copied from play.py with one or two modifications
# "Author": Joseph Britton (jtb8595)
#
@bp.route("/song/<int:song_id>", methods=["POST"])
@login_required
def play_song(song_id: int):
    print(request.form)
    curr_time = datetime.datetime.now()

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO listentosong (username, song_id, datetime_listened)
            VALUES (%s, %s, %s)
        """, (current_user.id, song_id, curr_time))
    
    conn.commit()

    return(redirect(url_for("popular.popular_genres")))


# HELPER FUNCTIONS

#
# A helper function that performs a select query and returns the results
# cursor: The database cursor to call the query from
# query: The string to use as the query
# Author: Joseph Britton (jtb8595)
#
def perform_select_query(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()

#
# A helper function that properly formats the results of a song query
# Author: Joseph Britton (jtb8595)
#
def format_song_query_results(select_array):
    song_ids = [] # The ids of songs added to results (and which index they're at)

    # results[x] = {id: song id, name: title, artist: artist name...
    # ..., length: length, listen_count: the listen count of the song}
    results = []

    # Construct the results
    for entry in select_array:
            # check if the song is not already in results
            if entry[0] not in song_ids:
                # Not in results - add it
                results.append({
                    "song_id": entry[0],
                    "name": entry[1], 
                    "artist": entry[2], 
                    "album": entry[3], 
                    "genre": entry[4],
                    "length": entry[5],
                    "release_date": entry[6],
                    "listen_count": entry[7]
                })

                # Add song id to running list of ids
                song_ids.append(entry[0])
            else:
                toCheck = results[song_ids.index(entry[0])]
                # In results - add the artist to song information if not already there
                if entry[2] not in toCheck['artist']:
                    results[song_ids.index(entry[0])]['artist'] += ", " + entry[2]
                # Do the same for album
                if entry[3] not in toCheck['album']:
                    results[song_ids.index(entry[0])]['album'] += ", " + entry[3]
                # Do the same for genre
                if entry[4] and entry[4] not in toCheck['genre']:
                    results[song_ids.index(entry[0])]['genre'] += ", " + entry[4]

    return results