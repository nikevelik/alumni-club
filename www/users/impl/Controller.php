<?php

require_once __DIR__ . '/Service.php';

class Controller {
  const HTTP_OK          = 200;
  const HTTP_CREATED     = 201;
  const HTTP_BAD_REQUEST = 400;
  const HTTP_NOT_FOUND   = 404;
  const HTTP_CONFLICT    = 409;

  const ERROR_STATUS = [
    Service::ERR_NOT_FOUND   => self::HTTP_NOT_FOUND,
    Service::ERR_EMAIL_TAKEN => self::HTTP_CONFLICT,
  ];

  public function get($request) {
    return self::respond(Service::get($request), self::HTTP_OK);
  }

  public function getAll($request = []) {
    return self::respond(Service::getAll($request), self::HTTP_OK);
  }

  public function post($request) {
    return self::respond(Service::create($request), self::HTTP_CREATED);
  }

  public function delete($request) {
    return self::respond(Service::delete($request), self::HTTP_OK);
  }

  public function patch($request) {
    return self::respond(Service::update($request), self::HTTP_OK);
  }

  private static function respond($result, $okStatus) {
    if (isset($result[Service::KEY_ERROR])) {
      $code = $result[Service::KEY_ERROR];
      http_response_code(self::ERROR_STATUS[$code] ?? self::HTTP_BAD_REQUEST);
    } else {
      http_response_code($okStatus);
    }
    return json_encode($result);
  }
}
