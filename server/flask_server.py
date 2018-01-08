from flask import Flask, request
app = Flask(__name__)

import sqlite3
database = "messages.db"

with sqlite3.connect(database) as conn:
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS balls (
            time_observed datetime,
            time_collected datetime,
            x real,
            y real,
            r real
        );""")
    conn.commit()

@app.route("/test", methods=["POST"])
def respond_test():
    print(request.json)
    return "OK"

@app.route("/balls", methods=["POST"])
def respond_balls():
    balls = request.json
    with sqlite3.connect(database) as conn:
        c = conn.cursor()
        c.executemany("""
            INSERT INTO balls VALUES (
                CURRENT_TIMESTAMP,
                NULL,
                :x,
                :y,
                :r
            );""", balls)
        conn.commit()
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True, port=8080)
