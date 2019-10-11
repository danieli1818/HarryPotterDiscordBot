import pymysql.cursors


def connect_database(host, user, password, db):

    # Connect to the database
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 db=db,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def is_valid(item):
    if type(item) is list or type(item) is tuple:
        for string in item:
            if '`' in string or '\'' in string or '"' in string:
                return False
        return True
    elif type(item) is str:
        return not ('`' in item or '\'' in item or '"' in item)
    else:
        return False


def is_valid_list_of_tuples(lst):
    if type(lst) is list:
        for tup in lst:
            if type(tup) is not tuple:
                return False
            for string in tup:
                if '`' in string or '\'' in string or '"' in string:
                    return False
        return True
    else:
        return False


class SQLInjectionException(Exception):
    """SQLInjection attempt has been recognized"""
    pass


def db_add_data(db, table: str, fields: list, fields_types: list, values: tuple):
    if not (is_valid(table) or is_valid(fields) or is_valid(fields_types) or is_valid(values)):
        raise SQLInjectionException
    try:
        with db.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `" + table + "` (`" + "`, `".join(fields) + "`) VALUES (" + ", ".join(fields_types) \
                  + ")"
            cursor.execute(sql, values)

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        db.commit()

        # with db.cursor() as cursor:
        #     # Read a single record
        #     sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
        #     cursor.execute(sql, ('webmaster@python.org',))
        #     result = cursor.fetchone()
        #     print(result)

    except Exception as e:
        print(e)

    finally:
        db.close()


def db_update_data_player(db, table: str, player_id: str, fields_and_values: list):
    if not (is_valid(table) or is_valid(player_id) or is_valid_list_of_tuples(fields_and_values)):
        raise SQLInjectionException
    try:
        with db.cursor() as cursor:
            # Create a new record
            update_strs = [str(t[0]) + " = " + str(t[1]) for t in fields_and_values]
            sql = "UPDATE " + table + " SET " + ", ".join(update_strs) + " WHERE id=" + str(player_id)
            cursor.execute(sql)

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        db.commit()

        # with db.cursor() as cursor:
        #     # Read a single record
        #     sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
        #     cursor.execute(sql, ('webmaster@python.org',))
        #     result = cursor.fetchone()
        #     print(result)

    except Exception as e:
        print(e)

    finally:
        db.close()

def db_get_data_player(db, table: str, player_id: str, fields: list):
    if not (is_valid(table) or is_valid(player_id) or is_valid(fields)):
        raise SQLInjectionException
    try:
        with db.cursor() as cursor:
            # Create a new record
            # update_strs = [str(t[0]) + " = " + str(t[1]) for t in fields_and_values]
            sql = "SELECT " + ", ".join(fields) + " FROM " + table + " WHERE id=" + str(player_id)
            cursor.execute(sql)
            result = cursor.fetchone()
            return result

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        # db.commit()

        # with db.cursor() as cursor:
        #     # Read a single record
        #     sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
        #     cursor.execute(sql, ('webmaster@python.org',))
        #     result = cursor.fetchone()
        #     print(result)

    except Exception as e:
        print(e)

    finally:
        db.close()

