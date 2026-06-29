<?php

class UploadHelper {
  const UPLOAD_DIR = __DIR__ . '/../../../uploads/';
  const MAX_BYTES = 65536;

  const ALLOWED_MIME_EXT = [
    'image/jpeg'    => 'jpg',
    'image/png'     => 'png',
    'image/gif'     => 'gif',
    'image/webp'    => 'webp',
    'image/svg+xml' => 'svg',
  ];

  const ERR_TOO_LARGE      = 'file_too_large';
  const ERR_INVALID_TYPE   = 'invalid_file_type';
  const ERR_UPLOAD_FAILED  = 'upload_failed';
  const ERR_NO_FILE        = 'no_file_uploaded';
  const ERR_NOT_WRITABLE   = 'uploads_dir_not_writable';

  public static function save($file) {
    if (!is_array($file) || !isset($file['error'])) {
      return ['error' => self::ERR_NO_FILE];
    }

    if ($file['error'] === UPLOAD_ERR_NO_FILE) {
      return ['error' => self::ERR_NO_FILE];
    }

    if ($file['error'] === UPLOAD_ERR_INI_SIZE || $file['error'] === UPLOAD_ERR_FORM_SIZE) {
      return ['error' => self::ERR_TOO_LARGE];
    }

    if ($file['error'] !== UPLOAD_ERR_OK) {
      return ['error' => self::ERR_UPLOAD_FAILED];
    }

    if (!is_uploaded_file($file['tmp_name'])) {
      return ['error' => self::ERR_UPLOAD_FAILED];
    }

    if ($file['size'] > self::MAX_BYTES) {
      return ['error' => self::ERR_TOO_LARGE];
    }

    $mime = self::detectMime($file['tmp_name']);
    if (!isset(self::ALLOWED_MIME_EXT[$mime])) {
      return ['error' => self::ERR_INVALID_TYPE];
    }

    if (!is_dir(self::UPLOAD_DIR) || !is_writable(self::UPLOAD_DIR)) {
      return ['error' => self::ERR_NOT_WRITABLE];
    }

    $ext = self::ALLOWED_MIME_EXT[$mime];
    $filename = self::uuidv4() . '.' . $ext;
    $destination = self::UPLOAD_DIR . $filename;

    if (!move_uploaded_file($file['tmp_name'], $destination)) {
      return ['error' => self::ERR_UPLOAD_FAILED];
    }

    return $filename;
  }

  public static function delete($filename) {
    if (!is_string($filename) || $filename === '') {
      return;
    }
    if (strpbrk($filename, "/\\") !== false || $filename === '.' || $filename === '..') {
      return;
    }
    $path = self::UPLOAD_DIR . $filename;
    if (is_file($path)) {
      @unlink($path);
    }
  }

  private static function detectMime($path) {
    if (function_exists('finfo_open')) {
      $finfo = finfo_open(FILEINFO_MIME_TYPE);
      $mime = finfo_file($finfo, $path);
      finfo_close($finfo);
      if ($mime) {
        return $mime;
      }
    }
    if (function_exists('mime_content_type')) {
      return mime_content_type($path) ?: '';
    }
    return '';
  }

  private static function uuidv4() {
    $data = random_bytes(16);
    $data[6] = chr((ord($data[6]) & 0x0f) | 0x40); // version 4
    $data[8] = chr((ord($data[8]) & 0x3f) | 0x80); // variant 10
    return vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
  }
}
