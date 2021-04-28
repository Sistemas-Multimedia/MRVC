

1. image_IPP_adaptive:

	1. Controlar la distorsión bloque a bloque usando diferentes
	   valores de *q_step* y usar la entropía como estimación del
	   bit-rate. Para cada bloque, elegir el *q_step* que haga que la
	   pendiente de los bloques de la imagen reconstruída RD coincida
	   entre los diferentes bloques. Evidéntemente, hay que usar un
	   codec entrópico que sea lossless.
	  
	2. Otra opción es usar el mismo q_step para todos los bloques ...
	
2. coef_IPP:

	1. Si queremos trasladar la anterior idea al caso en que cada
	   bloque tiene un único coeficiente, suponiendo que la
	   transformada espacial es ortogonal, hay que cuantizar cada coef
	   usando un q_step diferente y 
