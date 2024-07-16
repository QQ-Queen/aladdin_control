"""
Init logging
"""
import logging
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, 
                    datefmt=r"%Y-%m-%d %H:%M:%S")


"""
Insert current work directory to system path
"""
import sys
import os
module_path = os.path.abspath(os.getcwd())
if module_path not in sys.path:
    sys.path.insert(0, module_path)
    paths = '\n'.join(sys.path)
    logging.info(f'System path: \n{paths}')

from controller.aladdin import AladdinController

if __name__ == '__main__':
    aladdin_ctrl = AladdinController(timeout=30)
    aladdin_ctrl.get_all_infor(save_infor=True)