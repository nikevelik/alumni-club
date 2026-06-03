<?php

class SessionHelper {
  const KEY_USER_ID = 'user_id';

  // Single entry point for session_start() so cookie params, lifetime, and
  // SameSite policy stay in one place. Callers should invoke start() at the
  // top of any endpoint that reads or writes session state.
  public static function start() {
    if (session_status() === PHP_SESSION_ACTIVE) {
      return;
    }
    session_set_cookie_params([
      'lifetime' => 0,
      'path'     => '/',
      'domain'   => '',
      'secure'   => self::isHttps(),
      'httponly' => true,
      'samesite' => 'Lax',
    ]);
    session_start();
  }

  public static function currentUserId() {
    return isset($_SESSION[self::KEY_USER_ID]) ? (int)$_SESSION[self::KEY_USER_ID] : 0;
  }

  // Regenerate the session id on login to defeat session fixation.
  public static function setUserId($id) {
    session_regenerate_id(true);
    $_SESSION[self::KEY_USER_ID] = (int)$id;
  }

  public static function clear() {
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
      $params = session_get_cookie_params();
      setcookie(
        session_name(),
        '',
        time() - 42000,
        $params['path'],
        $params['domain'],
        $params['secure'],
        $params['httponly']
      );
    }
    session_destroy();
  }

  private static function isHttps() {
    if (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') {
      return true;
    }
    if (!empty($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
      return true;
    }
    return false;
  }
}
