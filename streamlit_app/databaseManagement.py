import sqlite3
import arrow
import polars as pl
import  os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_NAME = os.path.join(ROOT_DIR, 'streamlit_app', 'OFFICE.sqlite')



def get_connection():
    return sqlite3.connect(DB_NAME,check_same_thread=False)








def get_emp_ID(empCode:str):
    print("INSIDE",empCode)
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("""
        SELECT employeeID FROM Employees WHERE empCode=?""",(empCode,))
        empID = cursor.fetchone()
        conn.close()
        return empID
    except sqlite3.Error as e:
        print(e)



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




def clear_database(mode):
    try:
        conn=get_connection()
        cursor=conn.cursor()
        if mode==0:
            cursor.execute("""
            DELETE FROM Empolyees """)
            conn.commit()
            return True

        if mode==1:
            cursor.execute("""
            DELETE FROM Projects """)
            conn.commit()
            return True
    except sqlite3.IntegrityError as e:
        return f"IntegrityError: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"



def insert_Work_done(employeeID:int,projectWorkedonID:int,StartTime:str,endTime:str):
    try:
        print("HIT_insert")
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
        print("HIT_UPDATE")
        conn = get_connection()
        cursor = conn.cursor()

        # Step 1: Get the latest record for the employee
        cursor.execute("""
            SELECT HoursWorkedID FROM HOURSWORKED
            WHERE employeeID = ?
            ORDER BY HoursWorkedID DESC
            LIMIT 1
        """, (empolyeeID,))
        result = cursor.fetchone()

        if result is not None:
            hours_worked_id = result[0]  # ✅ consistent variable name

            # Step 2: Update that row
            cursor.execute("""
                UPDATE HOURSWORKED
                SET EndTime = ?, projectWorkedONID = ?
                WHERE HoursWorkedID = ?
            """, (endTime, projectWorkOnID, hours_worked_id))
            conn.commit()
            print(f"✅ Successfully updated HoursWorkedID = {hours_worked_id}")
        else:
            print(f"⚠️ No matching row found for employeeID = {empolyeeID}")

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
        print(start_str)
        print(end_str)

        start_time = arrow.get(f"{today} {start_str}", "YYYY-MM-DD HH:mm")
        end_time = arrow.get(f"{today} {end_str}", "YYYY-MM-DD HH:mm")
        if end_time < start_time:
            end_time = end_time.shift(days=1)

        worked_hours = round((end_time - start_time).total_seconds() / 3600, 2)
        if worked_hours>8:
            worked_hours=8
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



def add_project(productName:str,projectDescrption:str,clientName:str,productBudget:float,projectCode:str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO Projects(productName,projectDescription,clientName,projectBudget,projectCode) 
        VALUES (?,?,?,?,?)""",(productName,projectDescrption,clientName,productBudget,projectCode))
        conn.commit()
        return "success"

    except sqlite3.IntegrityError as e:
        return f"Integrity error: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()


def get_projects_code(project_name:str=""):
    try:
        conn=get_connection()
        cursor=conn.cursor()

        cursor.execute("""
        SELECT projectCode FROM Projects WHERE productName=?
        """, (project_name,))
        rows=cursor.fetchone()
        conn.close()
        return rows

    except sqlite3.Error as e:
        return f"Database error: {e}"



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





def delete_Project_or_delete_emp(projectCode:str="",emp_first_name:str="",emp_last_name:str="",mode:int=0):
    try:
        conn=get_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        if mode==0:

            cursor.execute(
            """
                DELETE FROM Projects WHERE projectCode =?
            """,(projectCode,)
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

def get_emp_name_by_code(emp_code:str):
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("""
        select firstName, lastName from Employees WHERE empCode=?
        
        """,(emp_code,))
        rows = cursor.fetchall()
        conn.close()
        firstName=rows[0][0]
        lastName=rows[0][1]
        return firstName, lastName
    except sqlite3.Error as e:
        print(e)
def get_emp_code():
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("""
        SELECT empcode FROM Employees
        """)
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    except sqlite3.Error as e:
        print(e)


def update_project_info(projectName:str,choiceToUpdate:str,newValue:str):
    print(choiceToUpdate)
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("""SELECT projectID FROM Projects WHERE productName=? """,(projectName,))
        result=cursor.fetchone()
        if result is None:
            f"❌ Project '{projectName}' not found."
        projectID=result[0]

        if choiceToUpdate == "Project Name":
            cursor.execute("""
            UPDATE Projects SET productName=? WHERE projectID=?
            """,(newValue,projectID))
            conn.commit()
        if choiceToUpdate == "Project Description":
            cursor.execute("""
            UPDATE Projects SET projectDescription=? WHERE projectID=?
            """,(newValue,projectID))
            conn.commit()

        if choiceToUpdate == "Client Name":
            cursor.execute("""UPDATE Projects SET clientName=? WHERE projectID=?""",(newValue,projectID))
            conn.commit()

        if choiceToUpdate == "Project Budget":
            money=float(newValue)
            cursor.execute("""UPDATE Projects SET projectBudget=? WHERE projectID=?""", (money, projectID))
            conn.commit()

        if choiceToUpdate=="Project Code":
            cursor.execute("""
            UPDATE Projects SET projectCode=? WHERE projectID=?
            """,(newValue,projectID))
            conn.commit()


    except sqlite3.IntegrityError as e:
        return f"Integrity error: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

def update_emp_info(first_name,last_name,dataToUpdate):
    try:
        conn=get_connection()
        cursor=conn.cursor()
        if type(dataToUpdate)==str:
            cursor.execute("UPDATE Employees SET email=? WHERE =? and lastName=?",(dataToUpdate,first_name,last_name))
            conn.commit()
        if type(dataToUpdate)==int:
            cursor.execute("UPDATE Employees SET ratePerHr=? WHERE firstName=? and lastName=?", (dataToUpdate, first_name, last_name))
            conn.commit()
    except sqlite3.IntegrityError as e:
        return f"Integrity error: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()


def insert_new_emp(firstName:str, lastName, email:str, role:str, empCode:str, ratePerHour:int, password:str):
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("""
        INSERT INTO Employees(firstName,lastName,email,role,empCode,ratePerHr,empPassword) VALUES (?,?,?,?,?,?,?)
        
        """, (firstName, lastName, email, role, empCode, ratePerHour, password))
        conn.commit()
        return "success"

    except sqlite3.IntegrityError as e:
        return f"Integrity error: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

def get_emp_password(empId:int):
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("""
        SELECT EmpPassword FROM Employees WHERE employeeID=?
        
        """,(empId,))
        rows=cursor.fetchone()
        conn.close()
        return rows[0]

    except sqlite3.Error as e:
        return f"Database error: {e}"


def get_project_id(productName:str):
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute(
        """SELECT projectID FROM Projects WHERE productName=?
        """,(productName,))
        rows = cursor.fetchone()
        conn.close()
        return rows

    except sqlite3.Error as e:
        print(e)

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

def get_people_who_worked_on_project(projectCode:str):
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("""
        SELECT DISTINCT firstName,lastName,empCode FROM HOURSWORKED H
        JOIN Projects P ON P.projectID=H.projectWorkedONID
        JOIN Employees E ON E.employeeID=H.employeeID
        WHERE p.projectCode=?
        
        """,(projectCode,))
        rows=cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        return f"Database error: {e}"

def get_project_info(projectCode:str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
               SELECT  productName,projectDescription,clientName FROM HOURSWORKED H
               JOIN Projects P ON P.projectID=H.projectWorkedONID
               JOIN Employees E ON E.employeeID=H.employeeID
               WHERE p.projectCode=?

               """, (projectCode,))
        rows = cursor.fetchone()
        conn.close()
        return rows
    except sqlite3.Error as e:
        return f"Database error: {e}"



def get_total_hours_worked_on_project(projectCode: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT SUM(totalHoursWorked) AS HOURS FROM HOURSWORKED H
        JOIN Projects P ON P.projectID=H.projectWorkedONID
        JOIN Employees E ON E.employeeID=H.employeeID
        WHERE p.projectCode=?
    
        """, (projectCode,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        return f"Database error: {e}"



def get_cost_per_project(projectCode: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT  sum((ratePerHr * totalHoursWorked)) as CostPerProject FROM HOURSWORKED H
               JOIN Projects P ON P.projectID=H.projectWorkedONID
               JOIN Employees E ON E.employeeID=H.employeeID
               WHERE p.projectCode=?;
        
        """,(projectCode,))
        rows = cursor.fetchone()
        conn.close()
        return rows[0]
    except sqlite3.Error as e:
        return f"Database error: {e}"

def get_remaining_budget(projectCode:str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT  projectBudget-sum((ratePerHr * totalHoursWorked)) as ReamainingBudget FROM HOURSWORKED H
               JOIN Projects P ON P.projectID=H.projectWorkedONID
               JOIN Employees E ON E.employeeID=H.employeeID
               WHERE p.projectCode=?;
        """,(projectCode,))
        rows = cursor.fetchone()
        conn.close()
        return rows[0]
    except sqlite3.Error as e:
        return f"Database error: {e}"


def retrieve_full_report(mode):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if mode == "all":
            cursor.execute("""
        SELECT
    p.projectCode,
    P.productName,
    E.empCode,
    E.firstName,
    E.lastName,
    E.ratePerHr,
    SUM(H.totalHoursWorked) AS totalHoursWorked,
    P.projectBudget,
    SUM(E.ratePerHr * H.totalHoursWorked) AS totalCost
FROM
    HOURSWORKED H
    JOIN Projects P ON P.projectID = H.projectWorkedONID
    JOIN Employees E ON E.employeeID = H.employeeID
GROUP BY
    P.productName,
    E.empCode,
    E.firstName,
    E.lastName,
    E.ratePerHr,
    P.projectBudget
        
        """)
            rows = cursor.fetchall()
            conn.close()
            return rows

        if mode=="Projects":
            cursor.execute("""
            SELECT
    P.projectCode,
    P.productName,
    P.projectDescription,
    P.projectBudget,
    P.projectBudget - SUM(E.ratePerHr * H.totalHoursWorked) AS remainingBudget,
    SUM(H.totalHoursWorked) AS totalHoursWorked,
    SUM(E.ratePerHr * H.totalHoursWorked) AS totalCost
FROM
    HOURSWORKED H
    JOIN Projects P ON P.projectID = H.projectWorkedONID
    JOIN Employees E ON E.employeeID = H.employeeID
GROUP BY
    P.projectCode,
    P.productName,
    P.projectBudget
            
   
            
            """)

            rows = cursor.fetchall()
            conn.close()
            return rows
    except sqlite3.Error as e:
        return f"Database error: {e}"

def get_CAD_and_engineer_hours(projectCode:str,retrieve:str):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if retrieve=="CAD":
            cursor.execute("""
            SELECT
            SUM(H.totalHoursWorked) AS TOTALHOURS
            FROM HOURSWORKED H
            JOIN Projects P ON P.projectID = H.projectWorkedONID
            JOIN Employees E ON E.employeeID = H.employeeID
            WHERE E.Role='CAD';
            """)
            rows = cursor.fetchone()
            conn.close()
            return rows[0]
        if retrieve=="Engineer":
            cursor.execute("""
            SELECT
            SUM(H.totalHoursWorked) AS TOTALHOURS
            FROM HOURSWORKED H
            JOIN Projects P ON P.projectID = H.projectWorkedONID
            JOIN Employees E ON E.employeeID = H.employeeID
            WHERE E.Role='Engineer';
            """)
            rows = cursor.fetchone()
            conn.close()
            return rows[0]
    except sqlite3.Error as e:
        return f"Database error: {e}"



def insert_into_project_cost_table(reason:str,amount:float,projectCode:str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
           INSERT INTO ProjectCosts(projectID,amount,description) VALUES (?,?,?)

           """, (projectCode,amount,reason))
        conn.commit()
        return "success"

    except sqlite3.IntegrityError as e:
        return f"Integrity error: {e}"
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()











