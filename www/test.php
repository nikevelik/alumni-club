<?php
$env = parse_ini_file('/var/www/.env');

$pdo = new PDO(
    'mysql:host=db;port=3306;dbname=' . $env['MYSQL_DATABASE'],
    $env['MYSQL_USER'],
    $env['MYSQL_PASSWORD']
);

$stmt = $pdo->query('SELECT message FROM test LIMIT 1');
$row = $stmt->fetch(PDO::FETCH_ASSOC);

header('Content-Type: application/json');
echo json_encode($row);
