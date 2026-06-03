<?php

require_once __DIR__ . '/Service.php';

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

  public function get($request) {
    return self::respond(function () use ($request) { return Service::get(0, $request); }, self::HTTP_OK);
  }

  public function getAll($request = []) {
    return self::respond(function () use ($request) { return Service::getAll(0, $request); }, self::HTTP_OK);
  }

  public function post($request, $files = []) {
    return self::respond(function () use ($request, $files) { return Service::create(0, $request, $files); }, self::HTTP_CREATED);
  }

  public function delete($request) {
    return self::respond(function () use ($request) { return Service::delete(0, $request); }, self::HTTP_OK);
  }

  public function patch($request, $files = []) {
    return self::respond(function () use ($request, $files) { return Service::update(0, $request, $files); }, self::HTTP_OK);
  }

  public function login($request) {
    return self::respond(function () use ($request) { return Service::login(0, $request); }, self::HTTP_OK);
  }

  public function logout($current_user_id) {
    return self::respond(function () use ($current_user_id) { return Service::logout($current_user_id); }, self::HTTP_OK);
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
