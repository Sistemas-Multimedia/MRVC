''' MRVC/QDWT.py '''

import config
import deadzone as Q
import debug

if config.transform == "DWT":
    import H_DWT as H

if config.transform == "LP":
    import H_LP as H

def E(E_k, video, k, q_step):
    debug.print("Error before Q", E_k.max(), E_k.min(), q_step)
    q_E_k = Q.quantize(E_k, q_step) # (d)
    debug.print("Error after Q", q_E_k.max(), q_E_k.min())
    H.write(q_E_k, video, k)
    dq_E_k = Q.dequantize(q_E_k, q_step) # (E.g)
    debug.print("Error after iQ", dq_E_k.max(), dq_E_k.min())
    return dq_E_k
