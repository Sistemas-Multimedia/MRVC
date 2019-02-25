# WAVELET CONTRIBUTION
Una transformación es **ortogonal** cuando los coeficientes generados por la transformación no están correlacionados.  
Una transformación es **orthonormal** si la normal de toda la base de una transformación ortogonal es una. Tiene como característica que preserva la energía, la energía de salida es la misma que la de entrada.    

Las transformaciones **biortogonales** no mantienen la energía.  
Las transformaciones biortogonales son las más utilizadas en la compresión de imágenes debido a su superior eficiencia frente a las ortogonales, ya que permiten poseer simultáneamente extensiones simétricas.
En el caso de que se usen filtros similares y ambos tengan extensiones simétricas el rendimiento entre las transformaciones ortogonales y las biortogonales es similar.

# REVIEW

Hemos utilizado como conjunto de pruebas una secuencia de imágenes negra que simula las distintas subbandas de una imágen (LL,LH,HL,HH).

El script implementado se encarga de calcular la ganancia de cada subbanda respecto a la subbanda HH en el proceso de reconstrucción de una secuencia de imágenes. Para ello para cada subbanda se convierten todos sus valores a 0, excepto un valor central de la subbanda a la que se quiere calcular la ganancia, que en ese caso se inicializa a 255 (pulso). Posteriomente, se reconstruye la imágen usando la transformada inversa y se calcula su energía. Este proceso se repite para la subbanda HH y finalmente se divide la energia obtenida de la primera fase entre la energía obtenida de la segunda fase, este valor resultante es la ganancia.

Para realizar los experimentos hemos usado un filtro no ortogonal, en concreto el filtro Reverse biorthogonal 3.5 (rbio3.5). Con este filtro la energía no se conserva, siendo la ganancia de la subbanda LL superior al resto ya que es donde se concentra la mayoría de la información de la imágen.

A continuación, se muestran las ganacias obtenidas al ejecutar el experimento:

* Ganancia LL &nbsp;&nbsp;--> 1,0000038640411728
* Ganancia HL &nbsp;--> 1,0000009087893984
* Ganancia LH &nbsp;--> 1,0000009087893982
* Ganancia HH --> 1,0




