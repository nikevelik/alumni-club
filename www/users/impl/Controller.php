<?php

require_once __DIR__ . '/Service.php';

class Controller {
  public function get($request) {
    $id = $request['id'] ?? null;
    $result = Service::get($id);
    return json_encode($result);
  }
}
