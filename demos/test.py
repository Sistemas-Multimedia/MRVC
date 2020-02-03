import shutil
import wget
import sys, getopt
import os
from subprocess import Popen, PIPE, check_output

N_ITERATIONS = 0
VIDEOFILE_NAME = 'test_video'
VIDEOFILE_URL = ''
DEFAULT_DIR = '/tmp/mcdwt/'
TMP_DIR = ''


def do_cleanup(tmp_dir):
   print('Limpiando directorio de trabajo: %s' % tmp_dir)
   if (os.path.exists(tmp_dir)):
      try:
         shutil.rmtree(tmp_dir)
      except:
         print('Error while deleting directory')
   os.makedirs(tmp_dir, exist_ok=True)


def download_file_to_folder(videofile_url, videofile_name):
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


def execute_mdwt(image_directory, gop):
   print('Ejecutando MDWT.py para %s imagenes' %str(gop))
   # MDWT.py -N $num_imgs -p /tmp/
   args = ['python3', '-O', 'MDWT.py', '-N', str(gop), '-p', image_directory]
   return execute_command(args)


def execute_mcdwt(image_directory, gop, n_iteration, predictor=1):
   print('Ejecutando MCDWT.py para imagenes %s, predictor %s, iteraciones %s' %(str(gop), str(predictor), str(n_iteration)))
   # !python3 -O MCDWT.py -N $num_imgs -P $predictor -p /tmp/ -T $iterations
   args = ['python3', '-O', 'MCDWT.py', '-N', str(gop - 1), '-P', str(predictor), '-p', image_directory, '-T',
           str(n_iteration)]
   return execute_command(args)


def execute_command(args, cmd=None, shell=False):
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
      elif suffix == "KB":
         b = int(b / 1024 ** 2)
      elif suffix == "KB":
         b = int(b / 1024 ** 3)
      elif suffix == "KB":
         b = int(b / 1024 ** 4)
      else:
         print('WRONG FORMAT: \'>%s<\', RETURNING KB' % suffix)
   else:
      raise ValueError("var: %s of type: \'%s\' is not an int" % (str(b), type(b)))
   return b

def prepare_current_iteration_directory(tmp_dir, curr_gop, gop):
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

def compress_mcdwt(tmp_dir, videofile_url, n_iterations, predictor=1, suffix='B'):
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
      print('actividad_01.py -n <N_ITERATIONS> -f <VIDEOFILE_URL> -d <TMP_DIR>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-h", "--help"):
         print('actividad_01.py -n <N_ITERATIONS> -f <VIDEOFILE_URL> -d <TMP_DIR>')
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

   uncompressed, compressed = compress_mcdwt(TMP_DIR, VIDEOFILE_URL, N_ITERATIONS)
   print(str(uncompressed))
   print(str(compressed))


if __name__ == "__main__":
   main(sys.argv[1:])

