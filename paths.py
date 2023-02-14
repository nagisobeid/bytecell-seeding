import os
import sys
MODULE_PATHS = os.getenv('MODULE_PATHS').split(',')

for path in MODULE_PATHS:
    print(f'Registering dynamic path : {path}')
    sys.path.insert( 0, path )