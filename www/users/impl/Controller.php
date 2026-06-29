<?php

require_once __DIR__ . '/Service.php';
require_once __DIR__ . '/SessionHelper.php';

class Controller {
  const HTTP_OK           = 200;
  const HTTP_CREATED      = 201;
  const HTTP_BAD_REQUEST  = 400;
  const HTTP_UNAUTHORIZED = 401;
  const HTTP_NOT_FOUND    = 404;
  const HTTP_CONFLICT     = 409;

  const ERROR_STATUS = [
    Service::ERR_NOT_FOUND           => self::HTTP_NOT_FOUND,
    Service::ERR_EMAIL_TAKEN         => self::HTTP_CONFLICT,
    Service::ERR_INVALID_CREDENTIALS => self::HTTP_UNAUTHORIZED,
    Service::ERR_NOT_LOGGED_IN       => self::HTTP_UNAUTHORIZED,
  ];

  const HTTP_INTERNAL_ERROR = 500;
  const ERR_INTERNAL = 'internal_error';

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

  public function delete($request) {
    return $this->respondAuthenticated(function ($uid) use ($request) {
      return Service::delete($uid, $request);
    }, self::HTTP_OK);
  }

  public function patch($request, $files = []) {
    return $this->respondAuthenticated(function ($uid) use ($request, $files) {
      return Service::update($uid, $request, $files);
    }, self::HTTP_OK);
  }

  public function logout() {
    return self::respond(function () {
      return Service::logout($this->current_user_id);
    }, self::HTTP_OK);
  }

  public function post($request, $files = []) {
    error_log('POST users request: ' . json_encode($request));
    error_log('POST users files: ' . json_encode(array_map(function ($f) {
      return [
        'name'  => $f['name']  ?? null,
        'type'  => $f['type']  ?? null,
        'size'  => $f['size']  ?? null,
        'error' => $f['error'] ?? null,
      ];
    }, $files)));
    return self::respond(function () use ($request, $files) {
      return Service::create(0, $request, $files);
    }, self::HTTP_CREATED);
  }

  public function login($request) {
    return self::respond(function () use ($request) {
      return Service::login(0, $request);
    }, self::HTTP_OK);
  }

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
      return json_encode([
        Service::KEY_ERROR => self::ERR_INTERNAL,
        'debug' => [
          'class'   => get_class($e),
          'message' => $e->getMessage(),
          'file'    => $e->getFile(),
          'line'    => $e->getLine(),
        ],
      ]);
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
