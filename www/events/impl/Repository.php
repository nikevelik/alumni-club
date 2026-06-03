<?php

require_once __DIR__ . '/SQLHelper.php';

class Repository {
  const GET_SQL = 'SELECT `id`, `date`, `name`, `details`, `creator` FROM `events` WHERE `id` = ?';
  const GET_ALL_SQL = 'SELECT `id`, `date`, `name`, `details`, `creator` FROM `events` ORDER BY `id`';
  const SEARCH_SQL = 'SELECT `id`, `date`, `name`, `details`, `creator` FROM `events` WHERE `name` LIKE ? ORDER BY `id`';
  const INSERT_SQL = 'INSERT INTO `events` (`date`, `name`, `details`, `creator`) VALUES (?, ?, ?, ?)';
  const DELETE_SQL = 'DELETE FROM `events` WHERE `id` = ?';
  const CREATOR_EXISTS_SQL = 'SELECT `id` FROM `users` WHERE `id` = ?';

  public static function get($id) {
    return SQLHelper::queryOne(self::GET_SQL, [$id]);
  }

  public static function getAll() {
    return SQLHelper::queryAll(self::GET_ALL_SQL);
  }

  public static function search($query) {
    return SQLHelper::queryAll(self::SEARCH_SQL, ['%' . $query . '%']);
  }

  public static function creatorExists($creatorId) {
    return !empty(SQLHelper::queryOne(self::CREATOR_EXISTS_SQL, [$creatorId]));
  }

  public static function create($event) {
    return SQLHelper::execute(self::INSERT_SQL, [
      $event['date'],
      $event['name'],
      $event['details'] ?? null,
      $event['creator'],
    ]);
  }

  public static function delete($id) {
    return SQLHelper::executeUpdate(self::DELETE_SQL, [$id]);
  }
}
