from mydb import getConnection

connection = getConnection()
username = str(input("User name: "))
password = str(input("Password: "))

def checkPass(str1,str2):
    if(str1 == str2):
        return True 
    else:
        return False
"""
try:
    conn = connection.cursor()
    conn.execute(
                "INSERT INTO test(username,password) VALUES(%s,%s)",
                (username,password),
            )
    connection.commit()

except Exception as e:
    print("Exception occured:{}".format(e))
    connection.rollback()
finally:
    conn.close()
"""

db = connection.cursor()
db.execute("SELECT * FROM test WHERE username = %s", (username,))
user = db.fetchone()

if user is None:
    print("Incorrect username.")
elif not checkPass(user['password'], password):
    print("Incorrect password.")

print(user['password'],password)