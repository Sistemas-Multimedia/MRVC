# WAVELET CONTRIBUTION
Una transformación es **ortogonal** cuando los coeficientes generados por la transformación no están correlacionados.  
Una transformación es **orthonormal** si la normal de toda la base de una transformación ortogonal es una. Tiene como característica que preserva la energía, la energía de salida es la misma que la de entrada.    

Las transformaciones **biortogonales** no mantienen la energía.  
Las transformaciones biortogonales son las más utilizadas en la compresión de imágenes debido a su superior eficiencia frente a las ortogonales, ya que permiten poseer simultáneamente extensiones simétricas.
En el caso de que se usen filtros similares y ambos tengan extensiones simétricas el rendimiento entre las transformaciones ortogonales y las biortogonales es similar.

# REVIEW

Hemos utilizado como conjunto de pruebas la secuencia de 5 imágenes del video stockholm.

Primero, para cada imágen la hemos descompuesto en subbandas (LL, LH, HL, HH). El script implementado se encarga de poner a 0 todos los coeficientes de la subbanda HH excepto un valor central que lo pone a 255 (pulso).
Posteriormente, se reconstruye la imágenes y se compara la energía de cada subbanda respecto a la de HH para obtener los valores de ganancia.

Además de calcular la ganacia respecto a la subbanda HH hemos realizado pruebas con el resto de subbandas con los siguientes resultados medios:

* HH: 
  * HL: &nbsp;&nbsp; 4,752
  * LH: &nbsp;12,081
  * LL: 442,058
      
* HL:
  * LH: &nbsp;&nbsp;2,541
  * LL: &nbsp;92,969
  
* LH:
  * LL: &nbsp;36,584

Por último realizamos una prueba aplicando el pulso a todas las subbandas excepto a la LL.

* HH, HL, LH:
  * LL: &nbsp;24,780
  
La ganancia tan elevada de la subbanda LL es debido a que está posee la mayor parte de la información de la imágen y modificar el resto de subbandas como hemos realizado en estos experimentos a penas tiene cambios apreciables cuando se recomponen la secuencias de imagenes.
