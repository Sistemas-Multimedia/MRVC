import shutil
import wget
import sys
import getopt
import os
from subprocess import Popen, PIPE, check_output
import numpy as np
import cv2

MIDRISE = 'midrise'
MIDTHREAD = 'midthread'
DEADZONE = 'deadzone'
QUANTIZIERS = [MIDRISE, MIDTHREAD, DEADZONE]
N_ITERATIONS = 0
VIDEOFILE_NAME = 'test_video'
VIDEOFILE_URL = ''
DEFAULT_DIR = '/tmp/mcdwt/'
TMP_DIR = ''
LOOP_STEP = 1
POWER_OF_TWO = True


def do_cleanup(tmp_dir):
   '''
   Clean working directory
   Parameters
   ----------
   tmp_dir - string dir location

   Returns
   -------
   none
   '''
   print('Limpiando directorio de trabajo: %s' % tmp_dir)
   if (os.path.exists(tmp_dir)):
      try:
         shutil.rmtree(tmp_dir)
      except:
         print('Error while deleting directory')
   os.makedirs(tmp_dir, exist_ok=True)


def download_file_to_folder(videofile_url, videofile_name):
   '''
   Download video to location and assign name to videofile
   Parameters
   ----------
   videofile_url - video url
   videofile_name - location and filename for the video

   Returns
   -------

   '''
   print('Descargando archivo: \'%s\' a \'%s\'' % (videofile_url, videofile_name))
   res = wget.download(videofile_url, out=videofile_name)
   print('\n')
   return res


def extract_frames(tmp_dir, gop, videofile):
   '''
   Extract frames using ffmpeg and rename generated images from 001..999 to 000..999
   Files will be placed in directory TMP_DIR/GOP
   Parameters
   ----------
   TMP_DIR - DIRECTORY FOR THE IMAGES
   GOP - GROUP OF IMAGES

   Returns
   -------
   base directory with original images
   '''
   print('Extrayendo %s imagenes a %s' % (str(gop), tmp_dir))
   # ffmpeg -hide_banner -loglevel info -i $file -vframes 9 $folder%03d.png &
   base_dir = tmp_dir + str(gop) + os.sep
   pattern_dir = base_dir + 'original' + os.sep
   os.makedirs(pattern_dir, exist_ok=True)
   pattern = pattern_dir + '%3d.png'
   args = ['ffmpeg', '-hide_banner', '-loglevel', 'info', '-i', videofile, '-vframes', str(gop), pattern]
   execute_command(args)

   # fix frame numbering
   for i in range(1, gop):
      from_file = pattern_dir + str(i).zfill(3) + '.png'
      to_file = pattern_dir + str(i - 1).zfill(3) + '.png'
      shutil.copy(from_file, to_file)

   # remove last file
   rmfile = pattern_dir + str(gop).zfill(3) + '.png'
   os.remove(rmfile)

   # copy originals to res directory where algorythm will be applied
   res_dir = base_dir + 'res' + os.sep
   shutil.copytree(pattern_dir, res_dir)
   return base_dir


def execute_mdwt(image_directory, gop, inverse=False):
   '''
   calls mcdwt algorythm
   Parameters
   ----------
   image_directory - location of the images to process
   gop - group of pictures (number of images to process)

   Returns
   -------
   POPEN object
   '''
   print('Ejecutando MDWT.py para %s imagenes inverse: %s' %(str(gop), str(inverse)))
   # MDWT.py -N $num_imgs -p /tmp/
   args = ['python3', '-O', 'MDWT.py', '-N', str(gop), '-p', image_directory]
   if inverse == True: args.append('-b')
   return execute_command(args)


def execute_mcdwt(image_directory, gop, n_iteration, predictor=1, inverse=False):
   '''

   Parameters
   ----------
   image_directory - location of the images to process
   gop - group of pictures (number of images to process)
   n_iteration - number of iterations
   predictor - predictor value

   Returns
   -------
   POPEN object
   '''
   print('Ejecutando MCDWT.py para imagenes %s, predictor %s, iteraciones %s inverse: %s' %(str(gop), str(predictor),
                                                                                            str(n_iteration), str(inverse)))
   # !python3 -O MCDWT.py -N $num_imgs -P $predictor -p /tmp/ -T $iterations
   args = ['python3', '-O', 'MCDWT.py', '-N', str(gop - 1), '-P', str(predictor), '-p', image_directory, '-T',
           str(n_iteration)]
   if inverse == True: args.append('-b')
   return execute_command(args)


def execute_command(args, cmd=None, shell=False):
   '''
   executes command in shell
   Parameters
   ----------
   args - command and arguments
   cmd - required for rm command
   shell - popen shell parameter

   Returns
   -------

   '''
   if cmd is None:
      p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=shell)
   else:
      p = Popen("%s %s" % (cmd, args), shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
   p.wait()
   return p


def get_dirsize(dir_path, suffix="B"):
   res = int(check_output(['du', '-sb', dir_path]).split()[0].decode('utf-8'))
   print('sizeof: %s: %s' % (dir_path, str(res)))
   return get_size_format(res, suffix=suffix)


def get_size_format(b, suffix="B"):
   '''
   Transform value in bytes (integer) into KB,MB,GB,TB
   Parameters
   ----------
   b - integer value in bytes
   suffix - KB,MB,GB,TB

   Returns
   -------
   integer value in B,KB,MB,GB,TB
   '''
   if isinstance(b, int):
      if suffix == "B":
         pass
      elif suffix == "KB":
         b = int(b / 1024)
      elif suffix == "MB":
         b = int(b / 1024 ** 2)
      elif suffix == "GB":
         b = int(b / 1024 ** 3)
      elif suffix == "TB":
         b = int(b / 1024 ** 4)
      else:
         print('WRONG FORMAT: \'>%s<\', RETURNING KB' % suffix)
   else:
      raise ValueError("var: %s of type: \'%s\' is not an int" % (str(b), type(b)))
   return b



def prepare_current_iteration_directory(tmp_dir, curr_gop, gop):
   '''
   Copy all the images to the directory for the current iteration and remove
   pictures that won't be processed for the current gop number
   Parameters
   ----------
   tmp_dir - working directory
   curr_gop - current gop number
   gop - total gop number

   Returns
   -------
   destination directory (string)
   '''
   srt_dir = tmp_dir + str(gop) + os.sep
   dst_dir = tmp_dir + str(curr_gop) + os.sep
   print('Copiando %s imagenes al directorio: %s' %(str(curr_gop), dst_dir))
   #os.makedirs(tmp_dir, exist_ok=True)
   shutil.copytree(srt_dir, dst_dir)
   #remove extra images
   for i in range(curr_gop, gop):
      rm_file_original = dst_dir + 'original' + os.sep + str(i).zfill(3) + '.png'
      rm_file_res = dst_dir + 'res' + os.sep + str(i).zfill(3) + '.png'
      os.remove(rm_file_original)
      os.remove(rm_file_res)
   return dst_dir


def quantize_image_function(input_path, output_path, q_step, quantize_algorithm):
   # Read image
   image = cv2.imread(input_path, -1)
   # Transformation needed because Vicente said in forum
   tmp = image.astype(np.float32)
   tmp -= 32768

   if quantize_algorithm == MIDRISE:
      image = np.floor(tmp / q_step).astype(np.int16) * q_step + (q_step / 2)
   elif quantize_algorithm == MIDTHREAD:
      image = np.round(tmp / q_step).astype(np.int16) * q_step
   elif quantize_algorithm == DEADZONE:
      image = (tmp / q_step).astype(np.int16).astype(np.int)
   else:
      image = (tmp / q_step).astype(np.int16) * q_step  # Vicente's quantizer.py algorithm

   # Transformation needed because Vicente said in forum
   tmp = image.astype(np.float32)
   tmp += 32768
   image = tmp.astype(np.uint16)

   # Write image quantizied
   cv2.imwrite(output_path, image)

def prepare_quantization_directories(tmp_dir, q_step=32):
   '''
   Copy images from mcdwt result algorithm into 3 directories for quantifier evaluation
   Parameters
   ----------
   dir - string working directory
   dir_arr - array of dir_names to copy res directory
   Returns
   -------
   array destination directories full paths
   '''
   print('PREPARE DIRECTORIES FOR QUANTIZATION')
   global DEFAULT_DIR
   if isinstance(tmp_dir, str):
      if (tmp_dir == ''): tmp_dir = DEFAULT_DIR
      if (not tmp_dir.endswith(os.sep)):
         tmp_dir += os.sep
      if len(QUANTIZIERS) > 0:
         directories = [name for name in os.listdir(tmp_dir) if os.path.isdir(os.path.join(tmp_dir, name))]
         res_dirs = []
         for dir in directories:
            curr_path = tmp_dir + dir + os.sep
            for d in QUANTIZIERS:
               src_dir = curr_path + 'res' + os.sep
               dst_dir = curr_path + d + os.sep
               #remove dst_dir if exists
               cmd = 'rm'
               args = '-rf %s' % dst_dir
               execute_command(args, cmd=cmd, shell=True)

               os.makedirs(dst_dir, exist_ok=True)
               res_dirs.append(dst_dir)
               print('creating directory: %s' %dst_dir)

         return res_dirs
      else:
         raise Exception('dir_arr cannot be empty')
   else:
      raise Exception('tmp_dir must be a string')

def mse(path_A, path_B):
   '''
   mean( (A-B)**2 )
   Parameters
   ----------
   path_A - A image path
   path_B - B image path

   Returns
   -------
   mse value
   '''
   # the 'Mean Squared Error' between the two images is the
   # sum of the squared difference between the two images;
   # NOTE: the two images must have the same dimension

   A = cv2.imread(path_A, -1)
   B = cv2.imread(path_B, -1)
   err = np.sum((A - B) ** 2)

   err /= float(A.shape[0] * A.shape[1])

   # return the MSE, the lower the error, the more "similar"
   # the two images are
   return err


def func_qstep(qstep):
   if POWER_OF_TWO == True:
      qstep = int(pow(2, qstep))
   return qstep

def quantisize_images(tmp_dir, videofile_url, n_iterations, predictor=2, suffix='B',q_step=None, min_qstep=1, max_qstep=6, normalize=False):
   global DEFAULT_DIR
   if min_qstep > max_qstep: min_qstep= max_qstep
   if max_qstep < min_qstep: max_qstep = min_qstep
   if q_step is not None: min_qstep = max_qstep = q_step
   if (tmp_dir == ''): tmp_dir = DEFAULT_DIR
   if not tmp_dir.endswith(os.sep): tmp_dir += os.sep
   # execute mdwt and mcdwt
   original, compressed = compress_mcdwt_once(tmp_dir, videofile_url, n_iterations, predictor=predictor, suffix=suffix)

   # prepare directories
   curr_dir = tmp_dir + str(pow(2, n_iterations)) + os.sep

   # get res directory path
   res_dir = curr_dir + 'res' + os.sep

   # read image names from res directory (compressed)
   img_arr = [name for name in os.listdir(res_dir) if (os.path.isfile(os.path.join(res_dir, name)) and name.endswith('.png'))]
   print('--------------------------------------------------------------------------------------------')
   print('cuantificando imagenes arrlength: %s' %(str(len(img_arr))))
   print('--------------------------------------------------------------------------------------------')
   # quantify images applying q_step 1..max_qstep
   for q_func in QUANTIZIERS:
      print('cuantificandor: %s ' % (q_func))
      for img_name in img_arr:
         src_image = res_dir + img_name
         #for qstep in range(min_qstep, max_qstep + 1):
         for qstep in range(min_qstep, max_qstep + 1, LOOP_STEP):
            qstep = func_qstep(qstep)

            dst_dir = curr_dir + q_func + os.sep + str(qstep).zfill(2) + os.sep + 'res' + os.sep
            os.makedirs(dst_dir, exist_ok=True)
            dst_image = dst_dir + img_name
            quantize_image_function(src_image, dst_image, qstep, q_func)
   print('--------------------------------------------------------------------------------------------')
   print('descopmrimiendo imagenes cuantificadas')
   print('--------------------------------------------------------------------------------------------')
   mse_values = {}
   mse_values[DEADZONE] = {}
   mse_values[MIDTHREAD] = {}
   mse_values[MIDRISE] = {}
   for q_func in QUANTIZIERS:
      #for qstep in range(min_qstep, max_qstep + 1):
      for qstep in range(min_qstep, max_qstep + 1, LOOP_STEP):
         qstep = func_qstep(qstep)

         mse_values[q_func][str(qstep)] = {}
         mse_values[q_func][str(qstep)]['mse'] = []
         mse_values[q_func][str(qstep)]['size'] = -1

         print('cuantificandor: %s, qstep: %s ' % (q_func, qstep))
         q_dir = curr_dir + q_func + os.sep + str(qstep).zfill(2) + os.sep
         qres_dir = q_dir + 'res' + os.sep
         qdst_dir = q_dir + 'decompressed' + os.sep

         print('copiando imagenes antes de descomprimir: %s -> %s' %(qres_dir, qdst_dir))
         shutil.copytree(qres_dir, qdst_dir)

         print('--------------------------------------------------------------------------------------------')
         print('calculando peso del directorio de las subbandas para q_func: %s, qstep: %s' % (q_func, qstep))
         #qdst_dir
         mse_values[q_func][str(qstep)]['size'] = get_dirsize(qdst_dir, suffix='B')

         #python3 -O MCDWT.py -P $predictor -p /tmp/ -b
         execute_mcdwt(qdst_dir, pow(2, n_iterations), n_iterations, predictor=predictor, inverse=True)
         #python3 -O MDWT.py -p /tmp/ -b
         execute_mdwt(qdst_dir, pow(2, n_iterations), inverse=True)
         print('eliminando subbandas (rm -rf ?????.png)')
         cmd = 'rm'
         args = '-rf %s?????.png' %qdst_dir
         execute_command(args, cmd=cmd, shell=True)
         print('--------------------------------------------------------------------------------------------')
         print('calculando mse para q_func: %s, qstep: %s' %(q_func, qstep))
         img_arr = [name for name in os.listdir(qdst_dir) if (os.path.isfile(os.path.join(qdst_dir, name)) and name.endswith('.png'))]
         print('directorio: %s' %qdst_dir)
         print(str(img_arr))

         for img_name in img_arr:
            img_A = curr_dir + 'original' + os.sep + img_name
            img_B = qdst_dir + img_name
            mse_val = mse(img_A, img_B)
            mse_values[q_func][str(qstep)]['mse'].append(mse_val)

         print(str(mse_values[q_func][str(qstep)]))
         print(str(np.mean(mse_values[q_func][str(qstep)]['mse'])))

         if normalize == True:
            print('--------------------------------------------------------------------------------------------')
            print('normalizando imagenes cuantificadas')
            print('--------------------------------------------------------------------------------------------')
            img_arr = [name for name in os.listdir(qdst_dir) if (os.path.isfile(os.path.join(qdst_dir, name)) and len(name)<8)]
            for img in img_arr:
               img = qdst_dir + img
               args = ['convert', '-normalize', img, img]
               execute_command(args)


   return mse_values

def compress_mcdwt_once(tmp_dir, videofile_url, n_iterations, predictor=1, suffix='B'):
   global DEFAULT_DIR
   if (tmp_dir == ''): tmp_dir = DEFAULT_DIR
   y_arr = []
   y1_arr = []

   if (n_iterations == 0):
      raise Exception("El número de iteraciones no puede ser igual a 0")
   # cleanup
   do_cleanup(tmp_dir)
   # download file
   videofile = tmp_dir + VIDEOFILE_NAME
   download_file_to_folder(videofile_url, videofile)

   # extract frames ONCE to folder
   all_images_dir = extract_frames(tmp_dir, pow(2, n_iterations), videofile)

   curr_gop = pow(2, n_iterations)
   curr_dir = all_images_dir
   res_dir = curr_dir + 'res' + os.sep
   # execute MDWT algorythm
   execute_mdwt(res_dir, curr_gop)
   # execute MCDWT algorythm
   execute_mcdwt(res_dir, curr_gop, n_iterations, predictor)

   # remove original files from compressed directory
   rm_pattern = res_dir + '???.png'
   cmd = 'rm'
   args = '-rf %s' % rm_pattern
   execute_command(args, cmd=cmd, shell=True)

   # calculate size of directories
   print('Calculando tamaño de directorios')
   original_dir = curr_dir + 'original' + os.sep
   y = get_dirsize(original_dir, suffix=suffix)
   y1 = get_dirsize(res_dir, suffix=suffix)
   y_arr.append(y)
   y1_arr.append(y1)
   return y_arr, y1_arr

def compress_mcdwt_iterative(tmp_dir, videofile_url, n_iterations, predictor=1, suffix='B'):
   '''
   Main function, executes the process of running all the steps to compress images
   and calculate the size of them before and after compression
   Parameters
   ----------
   tmp_dir - working directory to extract images from the video and do processing
   videofile_url - url of the video
   n_iterations - number of iterations for mcdwt
   predictor - predictor value
   suffix - suffix for directory size (default=B,KB,MB,GB)

   Returns
   -------
   Two arrays: original_sizes, compressed sizes
   '''
   global DEFAULT_DIR
   if (tmp_dir == ''): tmp_dir = DEFAULT_DIR
   y_arr = []
   y1_arr = []

   if (n_iterations == 0):
      raise Exception("El número de iteraciones no puede ser igual a 0")
   # cleanup
   do_cleanup(tmp_dir)
   # download file
   videofile = tmp_dir + VIDEOFILE_NAME
   download_file_to_folder(videofile_url, videofile)

   # extract frames ONCE to folder
   all_images_dir = extract_frames(tmp_dir, pow(2, n_iterations), videofile)

   for curr_iteration in range(1, n_iterations + 1):
      curr_gop = pow(2, curr_iteration)
      #prepare directory
      if curr_gop != pow(2, n_iterations):
         curr_dir = prepare_current_iteration_directory(tmp_dir, curr_gop, pow(2, n_iterations))
      else:
         curr_dir = all_images_dir

      # execute MDWT algorythm
      res_dir = curr_dir + 'res' + os.sep
      execute_mdwt(res_dir, curr_gop)
      # execute MCDWT algorythm
      execute_mcdwt(res_dir, curr_gop, curr_iteration, predictor)

      # remove original files from compressed directory
      rm_pattern = res_dir + '???.png'
      cmd = 'rm'
      args = '-rf %s' % rm_pattern
      execute_command(args, cmd=cmd, shell=True)

      # calculate size of directories
      print('Calculando tamaño de directorios')
      original_dir = curr_dir + 'original' + os.sep
      y = get_dirsize(original_dir, suffix=suffix)
      y1 = get_dirsize(res_dir, suffix=suffix)
      y_arr.append(y)
      y1_arr.append(y1)
   return y_arr, y1_arr


def main(argv):
   global TMP_DIR
   global N_ITERATIONS
   global VIDEOFILE_URL

   try:
      opts, args = getopt.getopt(argv, "hn:f:d:", ["n_iter=", "f_url=", "dir="])
   except getopt.GetoptError:
      print('mcdwt_evaluate.py -n <N_ITERATIONS> -f <VIDEOFILE_URL> -d <TMP_DIR>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-h", "--help"):
         print('mcdwt_evaluate.py -n <N_ITERATIONS> -f <VIDEOFILE_URL> -d <TMP_DIR>')
         sys.exit()
      elif opt in ("-n", "--n_iter"):
         N_ITERATIONS = int(arg)
      elif opt in ("-f", "--f_url"):
         VIDEOFILE_URL = arg
      elif opt in ("-d", "--dir"):
         if (os.path.exists(arg) and arg.startswith('/tmp/')):
            TMP_DIR = arg
         else:
            TMP_DIR = DEFAULT_DIR

   uncompressed, compressed = compress_mcdwt_iterative(TMP_DIR, VIDEOFILE_URL, N_ITERATIONS)

   print(str(uncompressed))
   print(str(compressed))


if __name__ == "__main__":
   main(sys.argv[1:])
