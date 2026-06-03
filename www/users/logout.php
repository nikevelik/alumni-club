<?php

require_once __DIR__ . '/impl/Controller.php';
require_once __DIR__ . '/impl/SessionHelper.php';

header('Content-Type: application/json');

SessionHelper::start();

$current_user_id = SessionHelper::currentUserId();

$controller = new Controller();
$body = $controller->logout($current_user_id);

// Always tear the session down on a successful logout. If the user wasn't
// logged in to begin with the controller already returned an error and we
// leave any (empty) session alone.
$result = json_decode($body, true);
if (is_array($result) && isset($result[Service::KEY_LOGGED_OUT])) {
  SessionHelper::clear();
}

echo $body;
