for y in 01 02 03 04 05 06 07 08 09 10 11 12 13
do
    geomorph/output/SAV/xyz/gdal_translate MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvsptss.xyz     geomorph/output/SAV/tif/MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvsptss.tif      &
    geomorph/output/SAV/xyz/gdal_translate MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvspsal.xyz     geomorph/output/SAV/tif/MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvspsal.tif      &
    geomorph/output/SAV/xyz/gdal_translate MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvprob_pres.xyz geomorph/output/SAV/tif/MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvprob_pres.tif  &
    geomorph/output/SAV/xyz/gdal_translate MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvprob_abs.xyz  geomorph/output/SAV/tif/MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvprob_abs.tif   &
    geomorph/output/SAV/xyz/gdal_translate MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvprob.xyz      geomorph/output/SAV/tif/MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvprob.tif       &
    geomorph/output/SAV/xyz/gdal_translate MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvdfl.xyz       geomorph/output/SAV/tif/MP2023_S07_G500_C000_U00_V00_SLA_O_$y_$y_W_SAV.csvdfl.tif        &
done