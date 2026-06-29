<?php

require_once __DIR__ . '/impl/Controller.php';
require_once __DIR__ . '/impl/SessionHelper.php';

header('Content-Type: application/json');

$controller = new Controller();
$body = $controller->logout();

$result = json_decode($body, true);
if (is_array($result) && isset($result[Service::KEY_LOGGED_OUT])) {
  SessionHelper::clear();
}

echo $body;
