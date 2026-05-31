<?php

require_once __DIR__ . '/Repository.php';

class Service {
  const KEY_PROFILE_PICTURE = 'profile_picture';
  const IMG_PREFIX = '/img/';

  public static function get($id) {
    if (!is_numeric($id) || (int)$id <= 0) {
      return [];
    }
    $user = Repository::get($id);
    if (!empty($user) && !empty($user[self::KEY_PROFILE_PICTURE])) {
      $user[self::KEY_PROFILE_PICTURE] = self::IMG_PREFIX . $user[self::KEY_PROFILE_PICTURE];
    }
    return $user;
  }
}
