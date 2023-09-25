<?php
$csvFile = '/csv/data_database.csv';
$csvData = [];
if (($handle = fopen($csvFile, 'r')) !== false) {
    while (($row = fgetcsv($handle)) !== false) {
        $csvData[] = $row;
    }
    fclose($handle);
}

$timestamps = [];
$diskData = [];

foreach ($csvData as $row) {
    $timestamp = $row[0];
    $disk = $row[1];
    $temperature = floatval($row[2]);
    $timestampUnix = strtotime($timestamp);
    $currentTimestamp = time();
    $twoDaysAgoTimestamp = $currentTimestamp - (48 * 3600);

    if ($timestampUnix >= $twoDaysAgoTimestamp && $timestampUnix <= $currentTimestamp) {
        if (!isset($diskData[$disk])) {
            $diskData[$disk] = [
                'label' => $disk,
                'data' => [],
            ];
        }

        $diskData[$disk]['data'][] = $temperature;

        if (!in_array($timestamp, $timestamps)) {
            $timestamps[] = $timestamp;
        }
    }
}

$averageTemperatures = [];
foreach ($diskData as $disk => $data) {
    $temperatures = $data['data'];
    $averageTemperature = array_sum($temperatures) / count($temperatures);
    $averageTemperatures[$disk] = $averageTemperature;
}
?>

<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Security-Policy" content="frame-ancestors 'self' *">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div style="width: 80%; margin: 0 auto;">
        <canvas id="temperatureChart"></canvas>
    </div>

    <script>
        var ctx = document.getElementById('temperatureChart').getContext('2d');
        var datasets = [];
        <?php foreach ($diskData as $disk) { ?>
            datasets.push({
                label: 'Disk <?= $disk['label'] ?> (Avg: <?= round($averageTemperatures[$disk['label']], 2) ?>°C)',
                data: <?= json_encode($disk['data']) ?>,
                borderColor: 'rgba(<?php echo rand(0, 255) ?>, <?php echo rand(0, 255) ?>, <?php echo rand(0, 255) ?>, 1)',
                borderWidth: 1,
                fill: false
            });
        <?php } ?>

        var data = {
            labels: <?= json_encode($timestamps) ?>,
            datasets: datasets
        };
        var config = {
            type: 'line',
            data: data,
            options: {
                scales: {
                    y: {
                        suggestedMin: 20, // Set the minimum value of the y-axis
                        suggestedMax: 50, // Set the maximum value of the y-axis
                    }
                }
            }
        };
        var temperatureChart = new Chart(ctx, config);
    </script>
</body>
</html>
