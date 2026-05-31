<?php

require_once __DIR__ . '/impl/Controller.php';

header('Content-Type: application/json');

$controller = new Controller();
echo $controller->patch($_POST);
