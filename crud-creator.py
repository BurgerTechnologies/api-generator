import mysql.connector
import os


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="mysql",
  database="lawncare"
)


'''
Creates a quick and dirty api based on tables from a database in the current working directory
'''


def getTypeLetter(typein):
    if "int" in typein or "double" in typein:
        return "i"
    else:
        return "s"


def createFile(location,input):
    f = open(location, "w")
    f.write(input)
    f.close()



def createCreate(query,types,questionmarks,columns,table):

    columnsArray = columns.split(',')
    fromGet = ""
    for column in columnsArray:
        fromGet = fromGet + """
            """ + column + " = $input['" + column[1:] + "'];"

    start = """<?php
    require_once './../login.php';
    $conn = new mysqli($hn, $un, $pw, $db);
    if($conn->connect_error) die("Can't Connect");

    if($_SERVER['REQUEST_METHOD'] === 'POST')
    {
        $inputJSON = file_get_contents('php://input');
        $input = json_decode($inputJSON, TRUE);

        """ + fromGet + """

        create($conn,""" + columns + """);
    }
    function create($conn,""" + columns + """)
    {
        $query = '""" + query + """';
        $stmt = $conn->prepare($query);
        $stmt->bind_param('""" + types + """',""" + questionmarks + """);
        
    """
    for input in columns.split(','):
        start = start + " " + input + "In = " + input + ";" + """
        """
    function = start + """
        $result = $stmt->execute();
        $stmt->close();
    }
    """
    location = os.path.join(parent_dir, 'api\\' ,table,'create.php') 
    createFile(location,function)


def createRead(command,id,types,table):
    outputs = '$' + columns.replace(',',',$')
    start = """<?php
    require_once './../login.php';
    $conn = new mysqli($hn, $un, $pw, $db);
    if($conn->connect_error) die("Can't Connect");

    if($_SERVER['REQUEST_METHOD'] === 'GET')
    {
        $inputJSON = file_get_contents('php://input');
        $input = json_decode($inputJSON, TRUE);

        $id = $input['id'];//$_GET['id'];
        read($conn,$id);
    }
    function read($conn,$""" + id + """)
    {
        $query = '""" + command + """';
        $stmt = $conn->prepare($query);
        $stmt->bind_param('""" + types + """',$""" + id + """In);
        
    """
    input = columns.split(',')[0]
    start = start + " $" + input + "In = $" + input + ";" + """
    """
    function = start + """
        $result = $stmt->execute();
        $out = array();
        $stmt->bind_result(""" + outputs + """);
        while($stmt->fetch())
        {
            $hold = new stdClass();
            """
    for column in columns.split(','):
        function = function + "$hold->" + column + " = $" + column + """;
            """

    function = function + """
            $out[] = $hold;
        }
        $stmt->close();
        if($result)
        {
            http_response_code(200);
            return $out;
        }else{
            http_response_code(400);
            return false;
        }
    }
    """
    location = os.path.join(parent_dir, 'api\\' ,table,'read.php') 
    createFile(location,function)


def createUpdate(command,columns,types,table):
    columnsArray = columns.split(',')
    fromPut = ""
    for column in columnsArray:
        fromPut = fromPut + """
            """ + column + " = $input['" + column[1:] + "'];"

    paramList = columns.replace(",","In,") + "In," + columns.split(',')[0] + "In"
    start = """<?php
    require_once './../login.php';
    $conn = new mysqli($hn, $un, $pw, $db);
    if($conn->connect_error) die("Can't Connect");

    if($_SERVER['REQUEST_METHOD'] === 'PUT')
    {
        $inputJSON = file_get_contents('php://input');
        $input = json_decode($inputJSON, TRUE);
        
        """ + fromPut + """

        update($conn,""" + columns + """);
    }

    function update($conn,""" + columns + """)
    {
        $query = '""" + command + """';
        $stmt = $conn->prepare($query);
        $stmt->bind_param('""" + types + """',""" + paramList + """);
        
    """
    for input in columns.split(','):
        start = start + " " + input + "In = " + input + ";" + """
        """
    function = start + """
        $result = $stmt->execute();
        $stmt->close();
    }
    """
    location = os.path.join(parent_dir, 'api\\' ,table,'update.php') 
    createFile(location,function)



def createDelete(command,id,types,table):
    start = """<?php
    require_once './../login.php';
    $conn = new mysqli($hn, $un, $pw, $db);
    if($conn->connect_error) die("Can't Connect");

    if($_SERVER['REQUEST_METHOD'] === 'DELETE')
    {
        $inputJSON = file_get_contents('php://input');
        $input = json_decode($inputJSON, TRUE);

        $id = $input['id'];
        delete($conn,$id);
    }
    function delete($conn,""" + id + """In)
    {
        $query = '""" + command + """';
        $stmt = $conn->prepare($query);
        $stmt->bind_param('""" + types + """',""" + id + """);
        
    """ + """ """ + id + """In = """ + id + """;""" + """
        """
    function = start + """
        $result = $stmt->execute();
        $stmt->close();
    }
    """
    location = os.path.join(parent_dir, 'api\\' ,table,'delete.php') 
    createFile(location,function)






mycursor = mydb.cursor()

mycursor.execute("show tables")

myresult = mycursor.fetchall()
tables = []
parent_dir = os.path.abspath(os.getcwd())
path = os.path.join(parent_dir,'api\\')
os.mkdir(path)
for x in myresult:
    mycursor.execute("describe " + x[0])
    resultTable = mycursor.fetchall()
    columns = []
    types = []
    path = os.path.join(parent_dir, 'api\\' ,x[0]) 
    os.mkdir(path) 
    for y in resultTable:
        columns.append(y[0])
        holdtype = getTypeLetter(y[1].decode("utf-8")) 
        types.append(holdtype)
    table = [x[0],columns,types]
    tables.append(table)
    
#insert into table(columns) values(questionmarks)
for z in tables:
    table = z[0]
    columnsPlain =','.join(str(x) for x in z[1])
    columns = '$' + ',$'.join(str(x) for x in z[1])
    types = ''.join(str(x) for x in z[2])
    id = z[1][0]
    questionmarks = ','.join("?" for x in z[1])
    inputs = ','.join("$" + str(x) + "In" for x in z[1])
    commnd = "insert into " + table + "(" + columnsPlain + ") values(" + questionmarks + ")"
    createCreate(commnd,types,inputs,columns,table)
    #print(commnd)

#select columns from table
for z in tables:
    table = z[0]
    columns = ','.join(str(x) for x in z[1])
    types = z[2][0]
    id = z[1][0]
    commnd = "select " + columns + " from " + table + " where " + id + "=?"
    createRead(commnd,id,types,table)
    #print(commnd)

#update table set columns=questionmark where id=?
for z in tables:
    table = z[0]
    columns = '$' + ',$'.join(str(x) for x in z[1])
    types = ''.join(str(x) for x in z[2])
    id = z[1][0]
    questionmarks = '=?,'.join(str(x) for x in z[1]) + "=?"
    command = "update " + table + " set " + questionmarks + " where " + id + "=?" 
    createUpdate(command,columns,types,table)
    #print(commnd)

#delete from table where id=?
for z in tables:
    table = z[0]
    columns = '$' + ',$'.join(str(x) for x in z[1])
    id = z[1][0]
    commnd = "delete from " + table + " where " + id + "=?" 
    createDelete(commnd,'$' + id,z[2][0],table)
    #print(commnd)


#SELECT id, first_name, last_name, phone, address FROM client WHERE 1
#INSERT INTO client(id, first_name, last_name, phone, address) VALUES (?,?,?,?,?)
#UPDATE client SET id=?,first_name=?,last_name=?,phone=?,address=?
#DELETE FROM client WHERE id=?