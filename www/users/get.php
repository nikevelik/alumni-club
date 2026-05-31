<?php

require_once __DIR__ . '/impl/Controller.php';

$controller = new Controller();
echo $controller->get($_REQUEST);
