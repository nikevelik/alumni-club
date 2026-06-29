<?php

require_once __DIR__ . '/impl/Controller.php';
require_once __DIR__ . '/impl/SessionHelper.php';

header('Content-Type: application/json');

// Capture the session-resolved current user id BEFORE the delete runs so we
// can detect self-deletion. Controller's constructor calls
// SessionHelper::start() so $_SESSION is live by this point.
$controller = new Controller();
$current_user_id = SessionHelper::currentUserId();

$body = $controller->delete($_POST);

// If the user just deleted their own account, the session is now pointing at
// a row that no longer exists. Tear it down so subsequent requests cleanly
// return 401 not_logged_in instead of leaving a "ghost" session that would
// authenticate as a user the database can't resolve.
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
