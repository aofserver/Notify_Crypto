import mysql.connector
from pydantic import BaseModel




class CMD(BaseModel):
  command: str

def ConnectorDB():
  return mysql.connector.connect(host="127.0.0.1",user="root",password="",database="Bitnoti")

def ReadDB(columns,fetchall):
  return [{columns[index][0]:column for index, column in enumerate(value)} for value in fetchall]

def Query(cmd:CMD):
  db = ConnectorDB()
  mycursor = db.cursor()
  sql_cmd = """{}""".format(cmd)
  mycursor.execute(sql_cmd)
  rows = ReadDB(mycursor.description,mycursor.fetchall())
  db.close()
  return rows

def RUN(cmd:CMD):
  db = ConnectorDB()
  mycursor = db.cursor()
  sql_cmd = """{}""".format(cmd)
  try:
    mycursor.execute(sql_cmd)
    db.commit()
    db.close()
    return True
  except:
    db.close()
    return False





