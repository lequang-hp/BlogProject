import pymysql.cursors

def getConnection():
    conn = pymysql.connect(host='localhost',
        user='root',
        password='123456',
        db='blog',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    return conn
