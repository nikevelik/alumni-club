<?php

require_once __DIR__ . '/impl/Controller.php';
require_once __DIR__ . '/impl/SessionHelper.php';

header('Content-Type: application/json');

$controller = new Controller();
$current_user_id = SessionHelper::currentUserId();

$body = $controller->delete($_POST);

$result = json_decode($body, true);
if (
  is_array($result) &&
  isset($result[Service::KEY_DELETED]) &&
  $current_user_id > 0 &&
  (int)$result[Service::KEY_DELETED] === $current_user_id
) {
  SessionHelper::clear();
}

echo $body;
