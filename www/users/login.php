<?php

require_once __DIR__ . '/impl/Controller.php';
require_once __DIR__ . '/impl/SessionHelper.php';

header('Content-Type: application/json');

// Controller's constructor calls SessionHelper::start() so $_SESSION is live
// by the time we read the response.
$controller = new Controller();
$body = $controller->login($_POST);
$result = json_decode($body, true);

// Only persist the session if the controller actually authenticated the user.
// On error responses the controller has already set an appropriate status code.
if (is_array($result) && !empty($result[Service::KEY_LOGGED_IN]) && !empty($result[Service::KEY_ID])) {
  SessionHelper::setUserId($result[Service::KEY_ID]);
}

echo $body;
