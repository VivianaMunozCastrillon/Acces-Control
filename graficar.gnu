set terminal png size 800,400 enhanced
set output 'detections.png'

# Fija manualmente la fecha (cámbiala según tus datos)
fecha = "2025-05-10"
set title sprintf("Detecciones de Sensores D5 y D6 - Fecha: %s", fecha)

set xlabel "Hora"
set ylabel "Estado (0 = Sin detección, 1 = Detectado)"
set grid
set datafile separator ","
set yrange [0:1.2]
set style fill solid

# Configuración del formato de tiempo
set timefmt "%Y-%m-%d %H:%M:%S"
set xdata time
set format x "%H:%M:%S"

# Graficar los datos
plot 'datos_procesados.txt' using 1:(strcol(2) eq "D5" ? $3 : 1/0) with impulses lw 3 lc "blue" title 'Sensor D5', \
     '' using 1:(strcol(2) eq "D6" ? $3 : 1/0) with impulses lw 3 lc "red" title 'Sensor D6'