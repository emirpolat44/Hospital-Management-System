import pyodbc
from datetime import datetime

connection = pyodbc.connect('Driver={SQL Server};'
                      'Server=CHANGE HERE!;'      # Sql server name
                      'Database=CHANGE HERE;'     # Datebase name
                      'Trusted_Connection=yes;')
cursor = connection.cursor() # We need cursor because when we need to read or write any data to sql, we should use cursor

print("Welcome to Hospital Management System, you must login\n")
tryagain = 5 # That is for login try attempt
correct_login = False

while tryagain > 0 and not correct_login:
    __id__ = input("Please enter your Username :")
    __pw__ = input("Please enter your Password :")

    # Query user information from the database
    cursor.execute("SELECT COUNT(*) FROM users WHERE u_name = ? AND u_passw = ?", (__id__, __pw__))
    count = cursor.fetchone()[0]

    if count == 1:
        print("Login is successful."+"\n"*10)
        correct_login = True
    else:
        print("Login failed. Please try again.\n")
        tryagain -= 1

if tryagain == 0:
    print("Your entry allowance has expired!\n")

print(("\t\t\t\t\tHOSPITAL MANAGEMENT SYSTEM\t\t\t\t\t\n\n")
      + "-"*60
      +"\n\t\t\t<<  1  >> Add New Appointment\n"
      +"\t\t\t<<  2  >> Add New Patient\n"
      +"\t\t\t<<  3  >> Add New Doctor\n"
      +"\t\t\t<<  4  >> Add Diagnosis Information\n"
      +"\t\t\t<<  5  >> Departments in Hospital\n"
      +"\t\t\t<<  6  >> Full History of the Patient\n"
      +"\t\t\t<<  7  >> List of All Appointments\n"
      +"\t\t\t<<  8  >> List of All Patients\n"
      +"\t\t\t<<  9  >> List of All Doctors\n"
      +"\t\t\t<<  0  >> Exit the Program\n"
      + "-"*60)

while True:
    def register_appointment():
        try:
            ppatients_id = int(input("Patient's ID: "))

            # Bring the departments and get the ID of the department for which the appointment is to be made from the user.
            cursor.execute("SELECT dep_id, dep_name FROM departments")
            department_rows = cursor.fetchall()

            if department_rows:
                print("\nDepartments")
                print("dep_id\tdep_name")
                for row in department_rows:
                    dep_id, dep_name = row
                    print(f"{dep_id}\t\t{dep_name}")

                departments_id = int(input("Choose a Department ID: "))

                # Get the doctors from the department.
                cursor.execute("SELECT doc_id, doc_name, doc_sname FROM doctors WHERE depart_id = ?", departments_id)
                doctors = cursor.fetchall()

                # Assign the selected department information to a variable.
                cursor.execute("SELECT dep_name FROM departments WHERE dep_id = ?", departments_id)
                dep_name = cursor.fetchone()[0]

                if doctors:
                    print("\nDoctors in this Department:")
                    print("doc_id\tdoc_name\tdoc_sname")
                    for doc_id, doc_name, doc_sname in doctors:
                        print(f"{doc_id}\t\t{doc_name}\t\t{doc_sname}")

                    doctor_choice = int(input("Choose a doctor (doc_id): "))

                    # Bring patient information.
                    cursor.execute("SELECT p_name, p_sname FROM patients WHERE p_id = ?", ppatients_id)
                    patient_row = cursor.fetchone()

                    if patient_row:
                        patients_name, patients_sname = patient_row

                        # Get date and time information.
                        appointment_datetime = input("Appointment Date and Time (YYYY-MM-DD HH:MM): ")

                        try:
                            appointment_datetime = datetime.strptime(appointment_datetime, '%Y-%m-%d %H:%M')
                        except ValueError:
                            print("Invalid date and time format. Please use YYYY-MM-DD HH:MM format.")
                            return

                        # Add the appointment booking.
                        cursor.execute("""
                             INSERT INTO appointments (patients_id, patients_name, patients_sname, doctor_id, doctor_name, doctor_sname, app_date)
                             VALUES (?, ?, ?, ?, ?, ?, ?)
                         """, (ppatients_id, patients_name, patients_sname, doctor_choice, doc_name, doc_sname,
                               appointment_datetime))
                        connection.commit()
                        print(f"\nPatient :{patients_name} {patients_sname}")
                        print(f"Department :{dep_name}")
                        print(f"Doctor :{doc_name} {doc_sname}")
                        print(f"Appointment Date and Time :{appointment_datetime}")
                        print("Appointment registered successfully.")
                    else:
                        print("\nPatient with the specified ID does not exist.")
                else:
                    print("No doctors found in this department.")
            else:
                print("No departments found in the database.")
        except Exception as e:
            print(f"Error: {e}")

    def register_patient():
        try:
            # Get patient information from the user
            pname, psname = input("Patient's Name and Surname :").split()
            page = input("Patient's age :")
            pphone = input("Patient's Phone Number :")
            paddress = input("Patient's Address :")

            with connection.cursor() as cursor:
                # Add Patient
                cursor.execute(
                    "INSERT INTO patients(p_name, p_sname, p_age, p_phone, p_address, p_date) VALUES(?,?,?,?,?,GETDATE())",
                    (pname, psname, page, pphone, paddress))
                connection.commit()
                print("Patient Successfully Added.")

        except ValueError:
            return "Invalid data input."

        except pyodbc.DatabaseError as e:
            return f"Error has occurred : {str(e)}"

    def register_doctor(connection, cursor):
        try:
            # Get doctor information from the user
            docname, docsname = input("Doctor's Name and Surname :").split()
            docage = input("Doctor's Birthdate :")
            docphone = input("Doctor's Phone Number :")
            docaddress = input("Doctor's Address :")

            # Show available departments and let the user choose one
            cursor.execute("SELECT dep_id, dep_name FROM departments")
            department_rows = cursor.fetchall()

            if department_rows:
                print("\nDepartments")
                print("dep_id\tdep_name")
                for row in department_rows:
                    dep_id, dep_name = row
                    print(f"{dep_id}\t\t{dep_name}")
                departments_id = int(input("Choose a Department ID: "))
                cursor.close()
            else:
                print("No departments available. Please add departments first.")
                return

            with connection.cursor() as cursor:
                # Add Doctor
                cursor.execute(
                    "INSERT INTO doctors(doc_name, doc_sname, depart_id, doc_phone, doc_birthdate, doc_address) VALUES(?,?,?,?,?,?)",
                    (docname, docsname, departments_id, docphone, docage, docaddress))
                connection.commit()
                cursor.close()
                print("Doctor Successfully Added.")

        except ValueError:
            print("Invalid data input. Please enter valid values.")

        except pyodbc.DatabaseError as e:
            print(f"An error occurred: {str(e)}")

    def add_diagnosis(connection):
        try:
            diag_patid = int(input("Patient's ID :"))
            diag_diagnos = input("Patient's Diagnosis :")
            diag_prescription = input("Patient's Prescription :")

            with connection.cursor() as cursor:
                # Patient control
                cursor.execute("SELECT COUNT(*) FROM patients WHERE p_id = ?", (diag_patid,))
                pat_count = cursor.fetchone()[0]

                if pat_count == 0:
                    return "Patient not found."

                # Adding a diagnosis
                cursor.execute("INSERT INTO diagnosis (pat_id, diag_diagnosis, diag_prescription) VALUES (?, ?, ?)",
                               (diag_patid, diag_diagnos, diag_prescription))
                connection.commit()

                print("Diagnosis successfully added.")

        except ValueError:
            return "An invalid data input."

        except pyodbc.DatabaseError as e:
            return f"Error has occurred : {str(e)}"

    def data_list(table_name):
        try:
            cursor = connection.cursor()

            # Pull data from table with a query
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)

            # Get column names and data
            column_names = [column[0] for column in cursor.description]
            data = cursor.fetchall()

            # Find the maximum width for each column
            column_widths = [len(name) for name in column_names]
            for i, row in enumerate(data):
                for j, value in enumerate(row):
                    column_widths[j] = max(column_widths[j], len(str(value)))

            # Print column names
            for i, name in enumerate(column_names):
                print(name.ljust(column_widths[i]), end='\t')
            print("\n" + '--' * sum(column_widths))

            # Print data
            for row in data:
                for i, value in enumerate(row):
                    print(str(value).ljust(column_widths[i]), end='\t')
                print()

        except pyodbc.DatabaseError as e:
            print(f"Error has occurred: {str(e)}")

    def diagnosis_history():
        try:
            ppatients_id = int(input("Patient's ID: "))

            with connection.cursor() as cursor:
                # Check if there is a patient in the Appointments table
                cursor.execute("SELECT COUNT(*) FROM appointments WHERE patients_id = ?", (ppatients_id,))
                appointment_count = cursor.fetchone()[0]

                if appointment_count == 0:
                    print("No patient appointment found.")
                    return

                # Get diagnosis and prescription information from the Diagnosis table
                cursor.execute("""                                                                                               
                    SELECT diag_diagnosis, diag_prescription                                                                     
                    FROM diagnosis                                                                                               
                    WHERE pat_id = ?                                                                                             
                """, (ppatients_id,))

                rows = cursor.fetchall()

                if rows:
                    # Print diagnosis and prescription information for the patient
                    for i, row in enumerate(rows, 1):
                        diagnosis, prescription = row
                        print(f"Diagnosis {i}: {diagnosis}")
                        print(f"Prescription {i}: {prescription}\n")
                else:
                    print("No patient appointment found.")

        except ValueError:
            print("An invalid data input.")

        except pyodbc.DatabaseError as e:
            print(f"Error has occurred: {str(e)}")

    __option__ = int(input("\nPlease, Choose from the following options :"))
    if(__option__ == 1):
        try:
            print("Appointment Register!\n")
            register_appointment()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            continue

    elif(__option__ == 2):
        try:
            print("Patient Register!\n")
            register_patient()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            continue

    elif (__option__ == 3):
        try:
            print("Doctor Register!\n")
            register_doctor(connection,cursor)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            continue

    elif(__option__ == 4):
        try:
            print("Add Diagnosis!\n")
            add_diagnosis(connection)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            continue

    elif(__option__ == 5):
        try:
            data_list("departments")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            continue

    elif(__option__ == 6):
        try:
            diagnosis_history()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            continue

    elif(__option__ == 7):
        try:
            data_list("appointments")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            continue

    elif(__option__ == 8):
        try:
            data_list("patients")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            continue

    elif(__option__ == 9):
        try:
            data_list("doctors")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            continue

    elif(__option__ == 0):
        break
    else:
        print("You have chosen the wrong option, try again please.")