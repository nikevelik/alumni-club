<?php

class SQLHelper {
  const ENV_FILE = '/var/www/.env';
  const DSN = 'mysql:host=db;port=3306;dbname=';
  const KEY_DATABASE = 'MYSQL_DATABASE';
  const KEY_USER = 'MYSQL_USER';
  const KEY_PASSWORD = 'MYSQL_PASSWORD';

  private static function makePDO() {
    $env = parse_ini_file(self::ENV_FILE);
    return new PDO(
      self::DSN . $env[self::KEY_DATABASE],
      $env[self::KEY_USER],
      $env[self::KEY_PASSWORD]
    );
  }

  public static function queryOne($sql, $params = []) {
    $pdo = self::makePDO();
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    return $stmt->fetch(PDO::FETCH_ASSOC) ?: [];
  }
}
