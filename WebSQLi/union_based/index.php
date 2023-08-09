<?php
    echo "Welcome";
    echo "<br />";
    //These are the defined authentication environment in the db service
    $host = 'localhost';
    $user = 'root';
    //database user password
    $pass = 'sql@123456';
    // database name
    $mydatabase = 'mysqli';
    // check the mysql connection status
    $conn = new mysqli($host, $user, $pass, $mydatabase);
    echo '<form action="index.php" method="post">';
    echo 'Name: <input type="text" name="name">';
    echo 'E-mail: <input type="text" name="email">' ;
    echo '<input type="submit">';
    echo '</form>';
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        $data = $_REQUEST['email'];
        echo "<br />";
if ($result = $conn->query( " SELECT name, company FROM customers WHERE company = '$data' ")) { #dynamic_query
            echo "<br/>";
            while($row = mysqli_fetch_array($result))
            {
                echo "<b>Name:</b> " . $row['name'] . " ";
                echo "<b>Company: </b>" . $row['company'] . "<br />";
                echo "<b>Email: </b>" . $row['email'] . "<br />";
            }
            echo "Returned rows are: " . $result -> num_rows;
        }
    }
    $conn->close();
 ?>