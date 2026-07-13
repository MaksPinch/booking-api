# import psycopg

# conn = psycopg.connect(
#     dbname="booking",
#     user="booking_user",
#     password="booking_pass",
#     host="localhost",
#     port="5432",
# )
# print("OK, connected")
# conn.close()

import psycopg

try:
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="booking",
        user="booking_user",
        password="booking_pass",
    )
    print("CONNECTED")
    conn.close()
except Exception as e:
    print(e)
