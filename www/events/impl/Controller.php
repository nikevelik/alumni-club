<?php

require_once __DIR__ . '/Service.php';
require_once __DIR__ . '/SessionHelper.php';

class Controller {
  const HTTP_OK           = 200;
  const HTTP_CREATED      = 201;
  const HTTP_BAD_REQUEST  = 400;
  const HTTP_UNAUTHORIZED = 401;
  const HTTP_NOT_FOUND    = 404;

  const ERROR_STATUS = [
    Service::ERR_NOT_FOUND         => self::HTTP_NOT_FOUND,
    Service::ERR_CREATOR_NOT_FOUND => self::HTTP_NOT_FOUND,
    Service::ERR_NOT_LOGGED_IN     => self::HTTP_UNAUTHORIZED,
  ];

  const HTTP_INTERNAL_ERROR = 500;
  const ERR_INTERNAL = 'internal_error';

  // Resolved once per request from $_SESSION. 0 means "no active session".
  // Every public method on this controller is auth-gated — the request is
  // rejected with 401 not_logged_in before reaching the service if 0.
  private $current_user_id;

  public function __construct() {
    SessionHelper::start();
    $this->current_user_id = SessionHelper::currentUserId();
  }

  public function get($request) {
    return $this->respondAuthenticated(function ($uid) use ($request) {
      return Service::get($uid, $request);
    }, self::HTTP_OK);
  }

  public function getAll($request = []) {
    return $this->respondAuthenticated(function ($uid) use ($request) {
      return Service::getAll($uid, $request);
    }, self::HTTP_OK);
  }

  public function post($request) {
    return $this->respondAuthenticated(function ($uid) use ($request) {
      return Service::create($uid, $request);
    }, self::HTTP_CREATED);
  }

  public function delete($request) {
    return $this->respondAuthenticated(function ($uid) use ($request) {
      return Service::delete($uid, $request);
    }, self::HTTP_OK);
  }

  // ---------- internals ----------

  // Auth-gated wrapper. Returns 401 not_logged_in immediately if there is
  // no active session, never reaching the service.
  private function respondAuthenticated($action, $okStatus) {
    if ($this->current_user_id <= 0) {
      http_response_code(self::HTTP_UNAUTHORIZED);
      return json_encode([Service::KEY_ERROR => Service::ERR_NOT_LOGGED_IN]);
    }
    $uid = $this->current_user_id;
    return self::respond(function () use ($action, $uid) { return $action($uid); }, $okStatus);
  }

  private static function respond($action, $okStatus) {
    try {
      $result = $action();
    } catch (Throwable $e) {
      error_log($e);
      http_response_code(self::HTTP_INTERNAL_ERROR);
      return json_encode([Service::KEY_ERROR => self::ERR_INTERNAL]);
    }
    if (isset($result[Service::KEY_ERROR])) {
      $code = $result[Service::KEY_ERROR];
      http_response_code(self::ERROR_STATUS[$code] ?? self::HTTP_BAD_REQUEST);
    } else {
      http_response_code($okStatus);
    }
    return json_encode($result);
  }
}
