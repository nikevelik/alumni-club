<?php

require_once __DIR__ . '/Repository.php';
require_once __DIR__ . '/UploadHelper.php';

class Service {
  const KEY_PROFILE_PICTURE = 'profile_picture';
  const IMG_PREFIX = '/uploads/';

  const KEY_NAME = 'name';
  const KEY_EMAIL = 'email';
  const KEY_PASSWORD = 'password';
  const KEY_PASSWORD_HASH = 'password_hash';
  const KEY_GRADUATION_YEAR = 'graduation_year';
  const KEY_ID = 'id';
  const KEY_ERROR = 'error';
  const KEY_FIELDS = 'fields';

  const REQUIRED_FIELDS = ['name', 'email', 'password'];
  // profile_picture is set via $_FILES, never as a string field — see handleUpload().
  const OPTIONAL_FIELDS = [
    'graduation_year', 'field_of_study', 'current_role',
    'company', 'location', 'bio',
  ];

  const ERR_MISSING_FIELDS  = 'missing_required_fields';
  const ERR_INVALID_EMAIL   = 'invalid_email';
  const ERR_EMAIL_TAKEN     = 'email_already_registered';
  const ERR_INVALID_YEAR    = 'invalid_graduation_year';
  const ERR_INVALID_ID      = 'invalid_id';
  const ERR_NOT_FOUND       = 'user_not_found';
  const ERR_NO_FIELDS       = 'no_fields_to_update';

  const KEY_DELETED = 'deleted';
  const KEY_UPDATED = 'updated';
  const KEY_QUERY = 'query';

  const PATCHABLE_FIELDS = [
    'name', 'email', 'password', 'graduation_year', 'field_of_study',
    'current_role', 'company', 'location', 'bio',
  ];

  const MIN_YEAR = 1900;
  const MAX_YEAR = 2100;

  public static function get($input) {
    $id = self::extractId($input);
    if ($id === null) {
      return self::error(self::ERR_INVALID_ID);
    }
    $user = Repository::get($id);
    if (empty($user)) {
      return self::error(self::ERR_NOT_FOUND);
    }
    return self::decorateUser($user);
  }

  public static function getAll($input = []) {
    $query = $input[self::KEY_QUERY] ?? null;
    $users = ($query !== null && $query !== '')
      ? Repository::search($query)
      : Repository::getAll();
    return array_map([self::class, 'decorateUser'], $users);
  }

  public static function create($input, $files = []) {
    $missing = self::findMissingFields($input, self::REQUIRED_FIELDS);
    if (!empty($missing)) {
      return self::errorWithFields(self::ERR_MISSING_FIELDS, $missing);
    }

    $validation = self::validateProfileFields($input, true);
    if ($validation !== null) {
      return $validation;
    }

    if (Repository::emailExists($input[self::KEY_EMAIL])) {
      return self::error(self::ERR_EMAIL_TAKEN);
    }

    $picture = self::handleUpload($files);
    if (is_array($picture) && isset($picture[self::KEY_ERROR])) {
      return $picture;
    }

    $user = self::buildNewUser($input, $picture);
    $id = Repository::create($user);
    return [self::KEY_ID => (int)$id];
  }

  public static function delete($input) {
    $id = self::extractId($input);
    if ($id === null) {
      return self::error(self::ERR_INVALID_ID);
    }
    $existing = Repository::get($id);
    if (empty($existing)) {
      return self::error(self::ERR_NOT_FOUND);
    }
    Repository::delete($id);
    if (!empty($existing[self::KEY_PROFILE_PICTURE])) {
      UploadHelper::delete($existing[self::KEY_PROFILE_PICTURE]);
    }
    return [self::KEY_DELETED => $id];
  }

  public static function update($input, $files = []) {
    $id = self::extractId($input);
    if ($id === null) {
      return self::error(self::ERR_INVALID_ID);
    }

    $patch = self::collectPatchableFields($input);
    $picture = self::handleUpload($files);
    if (is_array($picture) && isset($picture[self::KEY_ERROR])) {
      return $picture;
    }

    if (empty($patch) && $picture === null) {
      return self::error(self::ERR_NO_FIELDS);
    }

    $validation = self::validateProfileFields($patch, false);
    if ($validation !== null) {
      if (is_string($picture)) {
        UploadHelper::delete($picture);
      }
      return $validation;
    }

    $existing = Repository::get($id);
    if (empty($existing)) {
      if (is_string($picture)) {
        UploadHelper::delete($picture);
      }
      return self::error(self::ERR_NOT_FOUND);
    }

    if (isset($patch[self::KEY_EMAIL]) && Repository::emailTakenByOther($patch[self::KEY_EMAIL], $id)) {
      if (is_string($picture)) {
        UploadHelper::delete($picture);
      }
      return self::error(self::ERR_EMAIL_TAKEN);
    }

    if (is_string($picture)) {
      $patch[self::KEY_PROFILE_PICTURE] = $picture;
    }

    Repository::update($id, self::hashPasswordField($patch));

    if (is_string($picture) && !empty($existing[self::KEY_PROFILE_PICTURE])) {
      UploadHelper::delete($existing[self::KEY_PROFILE_PICTURE]);
    }
    return [self::KEY_UPDATED => $id];
  }

  // ---------- private helpers ----------

  private static function handleUpload($files) {
    if (!isset($files[self::KEY_PROFILE_PICTURE])) {
      return null;
    }
    $file = $files[self::KEY_PROFILE_PICTURE];
    if (is_array($file) && ($file['error'] ?? UPLOAD_ERR_NO_FILE) === UPLOAD_ERR_NO_FILE) {
      return null;
    }
    $result = UploadHelper::save($file);
    if (is_array($result)) {
      return [self::KEY_ERROR => $result['error']];
    }
    return $result;
  }

  private static function extractId($input) {
    $id = $input[self::KEY_ID] ?? null;
    if (!is_numeric($id) || (int)$id <= 0) {
      return null;
    }
    return (int)$id;
  }

  private static function error($code) {
    return [self::KEY_ERROR => $code];
  }

  private static function errorWithFields($code, $fields) {
    return [self::KEY_ERROR => $code, self::KEY_FIELDS => $fields];
  }

  private static function decorateUser($user) {
    if (!empty($user) && !empty($user[self::KEY_PROFILE_PICTURE])) {
      $user[self::KEY_PROFILE_PICTURE] = self::IMG_PREFIX . $user[self::KEY_PROFILE_PICTURE];
    }
    return $user;
  }

  private static function findMissingFields($input, $required) {
    $missing = [];
    foreach ($required as $field) {
      if (empty($input[$field])) {
        $missing[] = $field;
      }
    }
    return $missing;
  }

  private static function validateProfileFields($input, $emailRequired) {
    if ($emailRequired || isset($input[self::KEY_EMAIL])) {
      if (!filter_var($input[self::KEY_EMAIL], FILTER_VALIDATE_EMAIL)) {
        return self::error(self::ERR_INVALID_EMAIL);
      }
    }

    if (isset($input[self::KEY_GRADUATION_YEAR]) && $input[self::KEY_GRADUATION_YEAR] !== '') {
      $year = (int)$input[self::KEY_GRADUATION_YEAR];
      if ($year < self::MIN_YEAR || $year > self::MAX_YEAR) {
        return self::error(self::ERR_INVALID_YEAR);
      }
    }
    return null;
  }

  private static function collectPatchableFields($input) {
    $patch = [];
    foreach (self::PATCHABLE_FIELDS as $field) {
      if (isset($input[$field]) && $input[$field] !== '') {
        $patch[$field] = $input[$field];
      }
    }
    return $patch;
  }

  private static function buildNewUser($input, $picture) {
    $user = [
      self::KEY_NAME          => $input[self::KEY_NAME],
      self::KEY_EMAIL         => $input[self::KEY_EMAIL],
      self::KEY_PASSWORD_HASH => self::hashPassword($input[self::KEY_PASSWORD]),
    ];
    foreach (self::OPTIONAL_FIELDS as $field) {
      $user[$field] = isset($input[$field]) && $input[$field] !== '' ? $input[$field] : null;
    }
    $user[self::KEY_PROFILE_PICTURE] = is_string($picture) ? $picture : null;
    return $user;
  }

  private static function hashPassword($plain) {
    return hash('sha256', $plain);
  }

  private static function hashPasswordField($patch) {
    if (isset($patch[self::KEY_PASSWORD])) {
      $patch[self::KEY_PASSWORD_HASH] = self::hashPassword($patch[self::KEY_PASSWORD]);
      unset($patch[self::KEY_PASSWORD]);
    }
    return $patch;
  }
}
