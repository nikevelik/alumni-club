<?php

require_once __DIR__ . '/Repository.php';

class Service {
  const KEY_ID = 'id';
  const KEY_DATE = 'date';
  const KEY_NAME = 'name';
  const KEY_DETAILS = 'details';
  const KEY_CREATOR = 'creator';
  const KEY_ERROR = 'error';
  const KEY_FIELDS = 'fields';
  const KEY_QUERY = 'query';
  const KEY_DELETED = 'deleted';

  const REQUIRED_FIELDS = ['date', 'name', 'creator'];
  const OPTIONAL_FIELDS = ['details'];

  const ERR_MISSING_FIELDS    = 'missing_required_fields';
  const ERR_INVALID_DATE      = 'invalid_date';
  const ERR_INVALID_CREATOR   = 'invalid_creator';
  const ERR_INVALID_ID        = 'invalid_id';
  const ERR_NOT_FOUND         = 'event_not_found';
  const ERR_CREATOR_NOT_FOUND = 'creator_not_found';

  const DATE_FORMAT = 'Y-m-d';

  public static function get($current_user_id, $input) {
    $id = self::extractId($input);
    if ($id === null) {
      return self::error(self::ERR_INVALID_ID);
    }
    $event = Repository::get($id);
    if (empty($event)) {
      return self::error(self::ERR_NOT_FOUND);
    }
    return self::decorateEvent($event);
  }

  public static function getAll($current_user_id, $input = []) {
    $query = $input[self::KEY_QUERY] ?? null;
    $events = ($query !== null && $query !== '')
      ? Repository::search($query)
      : Repository::getAll();
    return array_map([self::class, 'decorateEvent'], $events);
  }

  public static function create($current_user_id, $input) {
    $missing = self::findMissingFields($input, self::REQUIRED_FIELDS);
    if (!empty($missing)) {
      return self::errorWithFields(self::ERR_MISSING_FIELDS, $missing);
    }

    $validation = self::validateEventFields($input);
    if ($validation !== null) {
      return $validation;
    }

    if (!Repository::creatorExists((int)$input[self::KEY_CREATOR])) {
      return self::error(self::ERR_CREATOR_NOT_FOUND);
    }

    $event = self::buildNewEvent($input);
    $id = Repository::create($event);
    return [self::KEY_ID => (int)$id];
  }

  public static function delete($current_user_id, $input) {
    $id = self::extractId($input);
    if ($id === null) {
      return self::error(self::ERR_INVALID_ID);
    }
    $rows = Repository::delete($id);
    if ($rows === 0) {
      return self::error(self::ERR_NOT_FOUND);
    }
    return [self::KEY_DELETED => $id];
  }

  // ---------- private helpers ----------

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

  private static function decorateEvent($event) {
    if (!empty($event) && isset($event[self::KEY_ID])) {
      $event[self::KEY_ID] = (int)$event[self::KEY_ID];
    }
    if (!empty($event) && isset($event[self::KEY_CREATOR])) {
      $event[self::KEY_CREATOR] = (int)$event[self::KEY_CREATOR];
    }
    return $event;
  }

  private static function findMissingFields($input, $required) {
    $missing = [];
    foreach ($required as $field) {
      if (!isset($input[$field]) || $input[$field] === '') {
        $missing[] = $field;
      }
    }
    return $missing;
  }

  private static function validateEventFields($input) {
    if (isset($input[self::KEY_DATE]) && $input[self::KEY_DATE] !== '') {
      $parsed = DateTime::createFromFormat(self::DATE_FORMAT, $input[self::KEY_DATE]);
      if (!$parsed || $parsed->format(self::DATE_FORMAT) !== $input[self::KEY_DATE]) {
        return self::error(self::ERR_INVALID_DATE);
      }
    }

    if (isset($input[self::KEY_CREATOR]) && $input[self::KEY_CREATOR] !== '') {
      if (!is_numeric($input[self::KEY_CREATOR]) || (int)$input[self::KEY_CREATOR] <= 0) {
        return self::error(self::ERR_INVALID_CREATOR);
      }
    }
    return null;
  }

  private static function buildNewEvent($input) {
    $event = [
      self::KEY_DATE    => $input[self::KEY_DATE],
      self::KEY_NAME    => $input[self::KEY_NAME],
      self::KEY_CREATOR => (int)$input[self::KEY_CREATOR],
    ];
    foreach (self::OPTIONAL_FIELDS as $field) {
      $event[$field] = isset($input[$field]) && $input[$field] !== '' ? $input[$field] : null;
    }
    return $event;
  }
}
