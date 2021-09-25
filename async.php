<?php
  header("content-type: application/json");

  $test = getallheaders();
  file_put_contents('async.txt', json_encode($test, JSON_PRETTY_PRINT));

  header("CPEE-CALLBACK: true");
  exit;
?>