<?php

require_once __DIR__ . '/SQLHelper.php';

class Repository {
  const GET_SQL = 'SELECT `id`, `name`, `email`, `graduation_year`, `field_of_study`, `current_role`, `company`, `location`, `bio`, `profile_picture` FROM `users` WHERE `id` = ?';
  const GET_ALL_SQL = 'SELECT `id`, `name`, `email`, `graduation_year`, `field_of_study`, `current_role`, `company`, `location`, `bio`, `profile_picture` FROM `users` ORDER BY `id`';
  const SEARCH_SQL = 'SELECT `id`, `name`, `email`, `graduation_year`, `field_of_study`, `current_role`, `company`, `location`, `bio`, `profile_picture` FROM `users` WHERE `email` LIKE ? ORDER BY `id`';
  const INSERT_SQL = 'INSERT INTO `users` (`name`, `email`, `password_hash`, `graduation_year`, `field_of_study`, `current_role`, `company`, `location`, `bio`, `profile_picture`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)';
  const EMAIL_EXISTS_SQL = 'SELECT `id` FROM `users` WHERE `email` = ?';
  const DELETE_SQL = 'DELETE FROM `users` WHERE `id` = ?';
  const UPDATABLE_COLUMNS = [
    'name', 'email', 'password_hash', 'graduation_year', 'field_of_study',
    'current_role', 'company', 'location', 'bio', 'profile_picture',
  ];
  const EMAIL_TAKEN_BY_OTHER_SQL = 'SELECT `id` FROM `users` WHERE `email` = ? AND `id` <> ?';

  public static function get($id) {
    return SQLHelper::queryOne(self::GET_SQL, [$id]);
  }

  public static function getAll() {
    return SQLHelper::queryAll(self::GET_ALL_SQL);
  }

  public static function search($query) {
    return SQLHelper::queryAll(self::SEARCH_SQL, ['%' . $query . '%']);
  }

  public static function emailExists($email) {
    return !empty(SQLHelper::queryOne(self::EMAIL_EXISTS_SQL, [$email]));
  }

  public static function emailTakenByOther($email, $id) {
    return !empty(SQLHelper::queryOne(self::EMAIL_TAKEN_BY_OTHER_SQL, [$email, $id]));
  }

  public static function create($user) {
    return SQLHelper::execute(self::INSERT_SQL, [
      $user['name'],
      $user['email'],
      $user['password_hash'],
      $user['graduation_year'] ?? null,
      $user['field_of_study'] ?? null,
      $user['current_role'] ?? null,
      $user['company'] ?? null,
      $user['location'] ?? null,
      $user['bio'] ?? null,
      $user['profile_picture'] ?? null,
    ]);
  }

  public static function delete($id) {
    return SQLHelper::executeUpdate(self::DELETE_SQL, [$id]);
  }

  public static function update($id, $fields) {
    $setClauses = [];
    $params = [];
    foreach (self::UPDATABLE_COLUMNS as $col) {
      if (array_key_exists($col, $fields)) {
        $setClauses[] = "`$col` = ?";
        $params[] = $fields[$col];
      }
    }
    if (empty($setClauses)) {
      return 0;
    }
    $params[] = $id;
    $sql = 'UPDATE `users` SET ' . implode(', ', $setClauses) . ' WHERE `id` = ?';
    return SQLHelper::executeUpdate($sql, $params);
  }
}
