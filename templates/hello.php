<?php
  header("content-type: application/json");

  $test = getallheaders();
  file_put_contents('async.txt', json_encode($test, JSON_PRETTY_PRINT));

  header("CPEE-CALLBACK: true");
  exit;
?>

<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dataset</title>
</head>
 <body>
    <form method='post' action='askuser_interface_backtoengine.php'>
      <input type='hidden' name='engine' value='<?= $head['Cpee-Callback'] ?>

      <p>User Interface about an Insurance case:</p>
      <table>
        <tr>
            {% if input %}
                <td>{{input.work}}</td>
            {% endif %}
        </tr>
      </table>

      <p>
        <button type="submit" name='decisionPartial' >View partial report </button>
      </p>
      <p>
        <button type="submit" name='decisionClose' >Finish viewing report </button>
      </p>

    </form>

 </body>
</html>
