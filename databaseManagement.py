import sqlite3
import arrow
import polars as pl
from duckdb.duckdb import cursor
from matplotlib.backend_tools import cursors



DB_NAME='OFFICE.db'

def get_connection():
    return sqlite3.connect(DB_NAME,check_same_thread=False)




def fetch_employees():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Employees ')
        rows=cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(e)


def insert_Work_done(employeeID:int,projectWorkedonID:int,StartTime:str,endTime:str):
    try:
        print("HIT")
        conn = get_connection()
        utc = arrow.utcnow()
        local = utc.to('Asia/Taipei')
        session_date=local.format("YYYY-MM-DD")
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO HOURSWORKED  (employeeID,projectWorkedOnID,StartTime,EndTime,sessionDate)
        VALUES (?,?,?,?,?)""",(employeeID,projectWorkedonID,StartTime,endTime,session_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        return f"Integrity error: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

def update_work_done(endTime: str, projectWorkOnID: int, empolyeeID: int):
    try:
        print("HIT_2")
        conn = get_connection()
        cursor = conn.cursor()

        # Step 1: Get the rowid of the most recent open session
        cursor.execute("""
            SELECT rowid FROM HOURSWORKED
            WHERE employeeID=? AND EndTime=''
            ORDER BY rowid DESC
            LIMIT 1
        """, (empolyeeID,))
        result = cursor.fetchone()

        if result:
            rowid = result[0]

            # Step 2: Update that specific row
            cursor.execute("""
                UPDATE HOURSWORKED
                SET EndTime=?, projectWorkedOnID=?
                WHERE rowid=?
            """, (endTime, projectWorkOnID, rowid))
            conn.commit()
            return True
        else:
            return "No open session found to update."

    except sqlite3.IntegrityError as e:
        return f"Integrity error: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

def get_times(employeeID: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT StartTime, EndTime
            FROM HOURSWORKED
            WHERE employeeID=?
            ORDER BY rowid DESC
        """, (employeeID,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(e)
        return []




def calculate_total_hours_worked(empID):
    try:
        print("HIT_3")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT StartTime,EndTime FROM HOURSWORKED WHERE employeeID=? LIMIT 1
        """,(empID,))
        rows=cursor.fetchall()

        today = arrow.now().format("YYYY-MM-DD")
        print(today)
        start_str = rows[0][0]
        end_str = rows[0][1]

        start_time = arrow.get(f"{today} {start_str}", "YYYY-MM-DD HH:mm")
        end_time = arrow.get(f"{today} {end_str}", "YYYY-MM-DD HH:mm")
        if end_time < start_time:
            end_time = end_time.shift(days=1)

        worked_hours = round((end_time - start_time).total_seconds() / 3600, 2)
        print(worked_hours)
        cursor.execute("""
                    UPDATE HOURSWORKED
                    SET totalHoursWorked = ?
                    WHERE employeeID  = ?
                """, (worked_hours, empID))
        conn.commit()

    except sqlite3.Error as e:
        print(e)



def get_table_names():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def add_project(productName:str,projectDescrption:str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO Projects(productName,projectDescription) VALUES (?,?)""",(productName,projectDescrption))
        conn.commit()

    except sqlite3.IntegrityError as e:
        return f"Integrity error: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

def remove_emp(name:str):
    print("TEST")


def get_employees():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT firstName, lastName FROM EMPLOYEES
        """)
        rows=cursor.fetchall()
        conn.close()
        return [f"{first} {last}" for first, last in rows]


    except sqlite3.Error as e:
        print(e)
        return []





def delete_Project_or_delete_emp(projectName:str="",emp_first_name:str="",emp_last_name:str="",mode:int=0):
    try:
        conn=get_connection()
        cursor = conn.cursor()

        if mode==0:

            cursor.execute(
            """
                DELETE FROM Projects WHERE productName=?
            """,(projectName,)
            )

        if mode==1:
            cursor.execute("""
            DELETE FROM Employees WHERE firstName=? AND lastName=?
            """,(emp_first_name,emp_last_name))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return f"Integrity error: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()


def get_project_names():
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute(
            """
            SELECT productName FROM Projects
            """
        )
        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows]

    except sqlite3.Error as e:
        print(e)

def insert_new_emp(firstName:str,lastName,email:str):
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("""
        INSERT INTO Employees(firstName,lastName,email) VALUES (?,?,?)
        
        """,(firstName,lastName,email))
        conn.commit()

    except sqlite3.IntegrityError as e:
        return f"Integrity error: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()


def convertDBToDataframe(tableName:str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if tableName == "Employees":
            cursor.execute(f"SELECT * FROM `{tableName}`")

        if tableName == "Projects":
            cursor.execute(f"SELECT * FROM `{tableName}`")

        if tableName == "HOURSWORKED":
            cursor.execute(f"SELECT employeeID,projectWorkedONID,StartTime,EndTime,totalHoursWorked FROM `{tableName}`")


        column_name=[description[0] for description in cursor.description]
        rows=cursor.fetchall()
        df=pl.DataFrame(rows,schema=column_name,orient="row")
        conn.close()
        return df

    except sqlite3.Error as e:
        print(e)





