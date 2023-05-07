from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

import sqlite3
from sqlite3 import Error
from flask import g

DATABASE = 'fantasy.db'

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
    except Error as e:
        print(e)
    return conn


def close_connection(conn):
    if conn is not None:
        conn.close()

def get_all_players():
    conn = get_db_connection()
    players = conn.execute('SELECT * FROM players').fetchall()
    close_connection(conn)
    return players


def get_all_objects():
    conn = get_db_connection()
    objects = conn.execute('SELECT * FROM objects').fetchall()
    close_connection(conn)
    return objects


def get_all_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    close_connection(conn)
    return categories


def get_all_points():
    conn = get_db_connection()
    points = conn.execute('SELECT * FROM points').fetchall()
    close_connection(conn)
    return points

def get_max_week():
    conn = get_db_connection()
    max_week = conn.execute('SELECT MAX(week) FROM points').fetchone()
    close_connection(conn)
    return max_week[0]

def get_player_points():
    conn = get_db_connection()
    player_points = conn.execute('SELECT p.id, p.name, SUM(c.points) FROM players p INNER JOIN objects o ON p.id = o.player_id INNER JOIN points pt ON o.id = pt.object_id INNER JOIN categories c ON pt.category_id = c.id GROUP BY p.id ORDER BY SUM(c.points) DESC').fetchall()
    close_connection(conn)
    return player_points

def get_player_objects():
    conn = get_db_connection()
    player_objects = conn.execute('SELECT p.id, o.id, o.name, o.eliminated FROM players p INNER JOIN objects o ON p.id = o.player_id ORDER BY p.id').fetchall()
    close_connection(conn)
    return player_objects

def get_object_points():
    conn = get_db_connection()
    object_points = conn.execute('SELECT o.id, pt.week, SUM(c.points) FROM objects o INNER JOIN points pt ON o.id = pt.object_id INNER JOIN categories c ON pt.category_id = c.id GROUP BY o.id, pt.week').fetchall()
    close_connection(conn)
    return object_points

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('fantasy.db')
    cur = conn.cursor()
    cur.execute(query, args)
    results = cur.fetchall()
    conn.commit()
    conn.close()
    return (results[0] if results else None) if one else results

@app.route('/players', methods=['GET', 'POST'])
def players():
    if request.method == 'POST':
        query_db('INSERT INTO players (name) VALUES (?)', (request.form['name'],))
        return redirect(url_for('players'))
    players = query_db('SELECT * FROM players')
    return render_template('players.html', players=players)

@app.route('/players/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    query_db('DELETE FROM players WHERE id=?', (player_id,))
    return redirect(url_for('players'))

@app.route('/objects', methods=['GET', 'POST'])
def objects():
    if request.method == 'POST':
        query_db('INSERT INTO objects (name, player_id) VALUES (?, ?)', (request.form['name'], request.form['player_id']))
        return redirect(url_for('objects'))
    objects = query_db('SELECT * FROM objects')
    players = query_db('SELECT * FROM players')
    return render_template('objects.html', objects=objects, players=players)

@app.route('/objects/delete/<int:object_id>', methods=['POST'])
def delete_object(object_id):
    query_db('DELETE FROM objects WHERE id=?', (object_id,))
    return redirect(url_for('objects'))

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        query_db('INSERT INTO categories (name, points) VALUES (?, ?)', (request.form['name'], request.form['points']))
        return redirect(url_for('categories'))
    categories = query_db('SELECT * FROM categories')
    return render_template('categories.html', categories=categories)

@app.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    query_db('DELETE FROM categories WHERE id=?', (category_id,))
    return redirect(url_for('categories'))

@app.route('/points', methods=['GET', 'POST'])
def points():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO points (object_id, category_id, week, notes) VALUES (?, ?, ?, ?)',
                     (request.form['object_id'], request.form['category_id'], request.form['week'], request.form['notes']))
        conn.commit()
        conn.close()

    conn = get_db_connection()
    points = conn.execute('SELECT points.id, objects.name, categories.name, points.week, points.notes, categories.points FROM points '
                          'JOIN objects ON points.object_id = objects.id '
                          'JOIN categories ON points.category_id = categories.id').fetchall()
    objects = conn.execute('SELECT * FROM objects').fetchall()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()

    return render_template('points.html', points=points, objects=objects, categories=categories)

@app.route('/delete_point/<int:point_id>', methods=['POST'])
def delete_point(point_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM points WHERE id = ?', (point_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('points'))

@app.route('/standings')
def standings():
    player_points = get_player_points()
    max_week = get_max_week()
    player_objects = get_player_objects()
    object_points = get_object_points()

    points_by_week = {}
    for obj_point in object_points:
        object_id = obj_point[0]
        week = obj_point[1]
        points = obj_point[2]

        if object_id not in points_by_week:
            points_by_week[object_id] = {}

        points_by_week[object_id][week] = points

    return render_template('standings.html', player_points=player_points, max_week=max_week, player_objects=player_objects, object_points=object_points, points_by_week=points_by_week)

@app.route('/')
def home():
    players = get_all_players()
    objects = get_all_objects()
    categories = get_all_categories()
    points = get_all_points()

    return render_template('home.html', players=players, objects=objects, categories=categories, points=points)


if __name__ == '__main__':
    app.run(debug=True)
