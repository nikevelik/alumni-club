<?php

require_once __DIR__ . '/Service.php';

class Controller {
  const HTTP_OK          = 200;
  const HTTP_CREATED     = 201;
  const HTTP_BAD_REQUEST = 400;
  const HTTP_NOT_FOUND   = 404;

  const ERROR_STATUS = [
    Service::ERR_NOT_FOUND         => self::HTTP_NOT_FOUND,
    Service::ERR_CREATOR_NOT_FOUND => self::HTTP_NOT_FOUND,
  ];

  const HTTP_INTERNAL_ERROR = 500;
  const ERR_INTERNAL = 'internal_error';

  public function get($request) {
    return self::respond(function () use ($request) { return Service::get($request); }, self::HTTP_OK);
  }

  public function getAll($request = []) {
    return self::respond(function () use ($request) { return Service::getAll($request); }, self::HTTP_OK);
  }

  public function post($request) {
    return self::respond(function () use ($request) { return Service::create($request); }, self::HTTP_CREATED);
  }

  public function delete($request) {
    return self::respond(function () use ($request) { return Service::delete($request); }, self::HTTP_OK);
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
