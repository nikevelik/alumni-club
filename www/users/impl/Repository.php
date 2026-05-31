<?php

require_once __DIR__ . '/SQLHelper.php';

class Repository {
  const GET_SQL = 'SELECT `id`, `name`, `email`, `graduation_year`, `field_of_study`, `current_role`, `company`, `location`, `bio`, `profile_picture` FROM `users` WHERE `id` = ?';

  public static function get($id) {
    return SQLHelper::queryOne(self::GET_SQL, [$id]);
  }
}
