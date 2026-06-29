<?php

require_once __DIR__ . '/impl/Controller.php';
require_once __DIR__ . '/impl/SessionHelper.php';

header('Content-Type: application/json');

$controller = new Controller();
$body = $controller->login($_POST);
$result = json_decode($body, true);

if (is_array($result) && !empty($result[Service::KEY_LOGGED_IN]) && !empty($result[Service::KEY_ID])) {
  SessionHelper::setUserId($result[Service::KEY_ID]);
}

echo $body;
