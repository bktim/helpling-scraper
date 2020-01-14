import psycopg2
from psycopg2.extras import execute_batch, execute_values


def insert_entries(entries):
    """
    Insert the entries into the database
    :param entries: list of dictionaries from client.py
    """
    query = "INSERT INTO entries (postcode, date, candidate_id, price_per_hour, avg_rating, firstname, shortname, default_profile_image, pets, windows, ironing, ratings_received_count, verification_level, documents, performed_cleanings_count, language_skills, instabook_enabled, experience_headline, experience_description) VALUES %s"
    template = "(%(postcode)s, %(date)s, %(id)s, %(price_per_hour)s, %(avg_rating)s, %(firstname)s, %(shortname)s,%(default_profile_image)s, %(pets)s,%(windows)s, %(ironing)s,%(ratings_received_count)s,%(verification_level)s,%(documents)s, %(performed_cleanings_count)s, %(language_skills)s, %(instabook_enabled)s, %(experience_headline)s, %(experience_description)s)"

    conn = psycopg2.connect(
        host='CHANGEME',
        port=5432,
        dbname='CHANGEME',
        user='CHANGEME',
        password='CHANGEME'
    )

    try:
        cur = conn.cursor()
        execute_values(cur, query, entries, template)
        conn.commit()
        print("Inserted values.")
        cur.close()
    except (IOError, psycopg2.DatabaseError) as error:
        return error
    finally:
        if conn is not None:
            conn.close()
