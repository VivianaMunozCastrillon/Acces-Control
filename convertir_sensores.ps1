Get-Content sensores.csv | ForEach-Object {
    $fields = $_ -split ","
    $fecha = $fields[0].Trim()
    $sensor = $fields[1].Trim()
    $estado = if ($fields[2].Trim() -eq "detectado") { 1 } else { 0 }
    "$fecha,$sensor,$estado"
} | Out-File datos_procesados.txt -Encoding ascii