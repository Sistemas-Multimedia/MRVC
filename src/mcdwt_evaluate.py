#!/usr/bin/env python3
#title           :mcdwt_evaluate.py
#description     :script for evaluation of mcdwt algorythm from repository: https://github.com/Sistemas-Multimedia/MCDWT
#author          :Nabel Hernandez Margin,
#                 Ángeles Garcia de las Heras,
#                 Manuel Gonzalez Rodriguez,
#                 Jose Carlos Fuentes Angulo,
#                 Viktor Sobolyev
#date            :06022020
#version         :0.3
#notes           :Script intended to be used on a linux machine. Not compatible with any Windows OS
#python_version  :3.5.1
#==============================================================================
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
HH = 'HH'
HL = 'HL'
LH = 'LH'
LL = 'LL'
SUBBANDS = [HH, HL, LH, LL]
N_ITERATIONS = 0
VIDEOFILE_NAME = 'test_video'
VIDEOFILE_URL = ''
DEFAULT_DIR = '/tmp/mcdwt/'
TMP_DIR = ''
LOOP_STEP = 1
POWER_OF_TWO = True
DEBUG = False #__debug__

def my_print(msg):
   if DEBUG:
      print(msg)

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
   my_print('Limpiando directorio de trabajo: %s' % tmp_dir)
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
   my_print('Descargando archivo: \'%s\' a \'%s\'' % (videofile_url, videofile_name))
   res = wget.download(videofile_url, out=videofile_name)
   my_print('\n')
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
   my_print('Extrayendo %s imagenes a %s' % (str(gop), tmp_dir))
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
   my_print('Ejecutando MDWT.py para %s imagenes inverse: %s' %(str(gop), str(inverse)))
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
   my_print('Ejecutando MCDWT.py para imagenes %s, predictor %s, iteraciones %s inverse: %s' %(str(gop), str(predictor),
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


def get_pathsize(path, suffix="B"):
   '''
   return dir/file size
   Parameters
   ----------
   path - file or folder path
   suffix - result size suffix ['B','MB','KB','GB','TB']

   Returns
   -------

   '''
   res = int(check_output(['du', '-sb', path]).split()[0].decode('utf-8'))
   my_print('sizeof: %s: %s' % (path, str(res)))
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
   my_print('Copiando %s imagenes al directorio: %s' %(str(curr_gop), dst_dir))
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
      image = (tmp / q_step).astype(np.int16) * q_step
   else:
      image = (tmp / q_step).astype(np.int16) * q_step  # Vicente's quantizer.py algorithm ///-> deadzone

   # Transformation needed because Vicente said in forum
   tmp = image.astype(np.float32)
   tmp += 32768
   image = tmp.astype(np.uint16)

   # Write image quantizied
   cv2.imwrite(output_path, image)

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

   return err

def func_qstep(qstep):
   if POWER_OF_TWO == True:
      qstep = int(pow(2, qstep))
   return qstep

def quantisize_images(tmp_dir, videofile_url, n_iterations, allsubbands=True, predictor=2, suffix='B', q_step=None, min_qstep=1, max_qstep=6, loopstep=None, powered_iterations=None, normalize=False):
   '''
   Runs quantization test for 3 defined algorithms (deadzone, midthread, midrise)
   Parameters
   ----------
   tmp_dir (str): directory for the algorythm to download video, extract images and subbands
   videofile_url (str): url of the videofile to extract images from
   n_iterations (int): value of the iterations for mcdwt algorythm
   predictor (int): value of the predictor for mcdwt algorythm
   suffix (str): suffix for the size of images, possible values: B, KB, MB, GB, TB
   q_step (int): start qstep iterations with value 1 and end with value q_step
   min_qstep (int): start qstep iterations with value
   max_qstep (int): end qstep iterations with value
   loopstep (int): value of qstep loop increment, default 1 (1,2,3,4,5...)
   powered_iterations (boolean) : if set to true, iterations of qstep for the quantisizer will be assigned a value of, qstep = 2^iteration_value
   normalize (boolean): normalizes images after finishing algorythm execution

   Returns
   -------
   json
   example to extract data from resulting json mse_value:
   def separate_msevalues_results(mse_values, mse_dz=[], mse_mr=[], mse_mt=[], size_dz=[], size_mr=[], size_mt=[]):
    # mse arrays
    # mse_dz = []#deadzone
    # mse_mr = []#midrise
    # mse_mt = []#midthread

    # x - q size values
    # size_dz = []
    # size_mr = []
    # size_mt = []
    for i in range(min_qstep, max_qstep + 1, LOOP_STEP):
        mse_dz.append(np.mean(mse_values['deadzone'][str(func_qstep(i))]['mse']))
        size_dz.append(mse_values['deadzone'][str(func_qstep(i))]['size'])

        mse_mr.append(np.mean(mse_values['midrise'][str(func_qstep(i))]['mse']))
        size_mr.append(mse_values['midrise'][str(func_qstep(i))]['size'])

        mse_mt.append(np.mean(mse_values['midthread'][str(func_qstep(i))]['mse']))
        size_mt.append(mse_values['midthread'][str(func_qstep(i))]['size'])
   '''
   global DEFAULT_DIR
   global POWER_OF_TWO
   global LOOP_STEP
   if loopstep is not None: LOOP_STEP = loopstep
   if powered_iterations is not None: POWER_OF_TWO = powered_iterations
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
   my_print('--------------------------------------------------------------------------------------------')
   my_print('cuantificando imagenes arrlength: %s' %(str(len(img_arr))))
   my_print('--------------------------------------------------------------------------------------------')
   # quantify images applying q_step 1..max_qstep
   for q_func in QUANTIZIERS:
      my_print('cuantificandor: %s ' % (q_func))
      for img_name in img_arr:
         src_image = res_dir + img_name
         #for qstep in range(min_qstep, max_qstep + 1):
         for qstep in range(min_qstep, max_qstep + 1, LOOP_STEP):
            qstep = func_qstep(qstep)

            dst_dir = curr_dir + q_func + os.sep + str(qstep).zfill(2) + os.sep + 'res' + os.sep
            os.makedirs(dst_dir, exist_ok=True)
            dst_image = dst_dir + img_name
            quantize_image_function(src_image, dst_image, qstep, q_func)
   my_print('--------------------------------------------------------------------------------------------')
   my_print('descopmrimiendo imagenes cuantificadas')
   my_print('--------------------------------------------------------------------------------------------')
   mse_values = {}
   mse_values[DEADZONE] = {}
   mse_values[MIDTHREAD] = {}
   mse_values[MIDRISE] = {}
   for q_func in QUANTIZIERS:
      #for qstep in range(min_qstep, max_qstep + 1):
      for qstep in range(min_qstep, max_qstep + 1, LOOP_STEP):
         qstep = func_qstep(qstep)

         mse_values[q_func][str(qstep)] = {}
         if allsubbands == True:
            mse_values[q_func][str(qstep)]['mse'] = []
            mse_values[q_func][str(qstep)]['size'] = -1
         else:
            mse_values[q_func][str(qstep)] = {}
            for sb in SUBBANDS:
               mse_values[q_func][str(qstep)][sb] = {
                  'mse': [],
                  'size': []
               }


         my_print('cuantificandor: %s, qstep: %s ' % (q_func, qstep))
         q_dir = curr_dir + q_func + os.sep + str(qstep).zfill(2) + os.sep
         qres_dir = q_dir + 'res' + os.sep
         qdst_dir = q_dir + 'decompressed' + os.sep

         my_print('copiando imagenes antes de descomprimir: %s -> %s' %(qres_dir, qdst_dir))
         shutil.copytree(qres_dir, qdst_dir)

         my_print('--------------------------------------------------------------------------------------------')
         my_print('calculando peso del directorio de las subbandas para q_func: %s, qstep: %s' % (q_func, qstep))
         #qdst_dir
         if allsubbands == True:
            mse_values[q_func][str(qstep)]['size'] = get_pathsize(qdst_dir, suffix='B')
         else:
            img_arr = [name for name in os.listdir(qres_dir) if (os.path.isfile(os.path.join(qres_dir, name)) and name.endswith('.png'))]
            for img_name in img_arr:
               img_A = curr_dir + 'res' + os.sep + img_name
               img_B = qdst_dir + img_name
               mse_val = mse(img_A, img_B)
               size = get_pathsize(img_B)
               for sb in SUBBANDS:
                  if img_name.startswith(sb):
                     mse_values[q_func][str(qstep)][sb]['mse'].append(mse_val)
                     mse_values[q_func][str(qstep)][sb]['size'].append(size)

         #python3 -O MCDWT.py -P $predictor -p /tmp/ -b
         execute_mcdwt(qdst_dir, pow(2, n_iterations), n_iterations, predictor=predictor, inverse=True)
         #python3 -O MDWT.py -p /tmp/ -b
         execute_mdwt(qdst_dir, pow(2, n_iterations), inverse=True)
         my_print('eliminando subbandas (rm -rf ?????.png)')
         cmd = 'rm'
         args = '-rf %s?????.png' %qdst_dir
         execute_command(args, cmd=cmd, shell=True)
         my_print('--------------------------------------------------------------------------------------------')
         my_print('calculando mse para q_func: %s, qstep: %s' %(q_func, qstep))
         img_arr = [name for name in os.listdir(qdst_dir) if (os.path.isfile(os.path.join(qdst_dir, name)) and name.endswith('.png'))]
         my_print('directorio: %s' %qdst_dir)
         my_print(str(img_arr))

         if allsubbands == True:
            for img_name in img_arr:
               img_A = curr_dir + 'original' + os.sep + img_name
               img_B = qdst_dir + img_name
               mse_val = mse(img_A, img_B)
               mse_values[q_func][str(qstep)]['mse'].append(mse_val)

         if normalize == True:
            my_print('--------------------------------------------------------------------------------------------')
            my_print('normalizando imagenes cuantificadas')
            my_print('--------------------------------------------------------------------------------------------')
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
   my_print('Calculando tamaño de directorios')
   original_dir = curr_dir + 'original' + os.sep
   y = get_pathsize(original_dir, suffix=suffix)
   y1 = get_pathsize(res_dir, suffix=suffix)
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
      my_print('Calculando tamaño de directorios')
      original_dir = curr_dir + 'original' + os.sep
      y = get_pathsize(original_dir, suffix=suffix)
      y1 = get_pathsize(res_dir, suffix=suffix)
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

if __name__ == "__main__":
   main(sys.argv[1:])
