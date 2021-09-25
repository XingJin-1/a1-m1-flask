<?php
  $conf = json_decode(file_get_contents('async.txt'));
  $cb = $conf->{'Cpee-Callback'};

  $opts = array('http' =>
    array(
      'method' => 'PUT',
      'header' =>
        "Content-type: application/json\r\n" .
        "CPEE-UPDATE: true\r\n" .
        "Accept: application/json\r\n" ,
      'content' => '{ "x": 1, "y": 7 }'
    )
  );
  $context = stream_context_create($opts);
  $result = file_get_contents($cb,false,$context);
?>