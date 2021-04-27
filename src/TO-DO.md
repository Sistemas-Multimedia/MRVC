1. The residue is perfect is all the values are 0. Only statistical redundancy needs to be removed.

1. All the residues in a GOP can be compressed as a 3D structure. Motion information could be used to increase the locality.

1. Temporal stability (S-type blocks) can be obtained generating zeros at the residue. Selective quantization of the residue blocks/coefs can be the key.

1. YCoCg should be used only if the original domain is RGB. If the original domain is YCbCr, no color transform should be used.

1. No chroma subsampling is considered, but oviously the chroma information can be low-pass filtered.

1. If the ME is good, the interference between blocks is small. Therefore, the contribution of a block/coef to the quality of the GOP can be considered independent, and the RD tradeoff can be optimized independtly for each block/coef.

1. Relative block/coef distortion = (energy of the block/coef residue) / (energy of the original block/coef)

1. Adaptive block/coef quantization (each block/coef with a different q_step):
   1. For each residue block/coef:
	  1. Use the same q_step and compute the distortion.
	  2. Compute the rate (entropy) of the residue block.
	  3. Compute the rate of the residue (quantized) block.
	  4. Compute the RD-slope = (Delta D)/(Delta R), where the increments are measured from the unquantized blocks.
   2. Discretize (quantize) the slopes to 8 bits.
   3. Find the slope* that is repeated the most.
   4. For each residue block/coef:
	  1. While slope < slope*, increase the corresponding q_step, and recompute the slope.
	  2. While slope > slope*, decrease the corresponding q_step, and recompute the slope.
	  
1. Block-type decission (through quantization of the prediction):
   1. For each prediction block:
	  1. Compute the residue.
	  2. Find the q_step that minimizes the rate of the residue. Notice that if q_step is high, the prediction is bad and the type is I. If q_step = 1, the prediction is perfect and the type is S. Otherwise, the type is P.

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
