import os 
import subprocess
import vpype as vp
from vpype_cli import execute
import contextlib
import io

import vpype_cli

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)

socketio = SocketIO(app)

def convert_file(file, outputsize = 'a4',  pageorientation = 'landscape', device = 'hp7475a', speed = '', custom_comand = '', linemerge  = '', linesort = '', linesimplify = '', reloop = ''):
    if file:
        print('Converting file: ' + file)

        filename, file_extension = os.path.splitext(file)
        vpype_options =""
        args = ''
        doc = vp.Document()

        # args += ' read "' + os.getcwd() + '/' + str(file) + '"'; #Read input svg

        doc = execute("read " + os.getcwd() + '/' + str(file) )

        # Scale svg to desired paper size
        if (pageorientation == 'landscape'):
            args += ' eval w,h=gprop.vp_page_size crop 0 0 %w% %h% rect -l1000 0 0 %w% %h% layout -l -m  0 ' + outputsize + ' ldelete 1000';

        else:
            args += ' eval w,h=gprop.vp_page_size crop 0 0 %w% %h% rect -l1000 0 0 %w% %h% layout -m  0 ' + outputsize + ' ldelete 1000';

        # Vpype optimise 

        if custom_comand :
            vpype_options += " " + custom_comand ;
            args += " " + custom_comand + " "

        else :    

            if linemerge :
                args += ' linemerge --tolerance 0.2mm';
                vpype_options +="-linemrge"

            if linesimplify :
                args += ' linesimplify --tolerance 0.1mm';
                vpype_options +="-linesimplify"

            if reloop :
                args += ' reloop';
                vpype_options +="-reloop"
                
            if linesort :
                args += ' linesort';
                vpype_options +="-linesort"            

        args += ' write --device ' + str(device);

        args += ' --page-size ' + str(outputsize);

        if speed is not None and speed.isnumeric():
            args += ' -vs ' + str(speed)

        if (pageorientation == 'landscape'):
            args += ' --landscape';

        outputFile = filename + '-' + outputsize + '-' + pageorientation + vpype_options + '-' + device  + '.hpgl'

        args += ' --center';
        args += ' "' + os.getcwd() + '/' + str(outputFile) + '"'

        # result = execute(args, doc)


        # if result == "error":
        #     output = output.partition("Error:")[2]
        #     socketio.emit('status_log', {'data': 'File not converted.'})
        #     socketio.emit('status_log', {'data': output})
        #     return 'File not converted.'
        # else:
        #     socketio.emit('status_log', {'data': 'File converted.'})
        #     return 'Exported ' + str(outputFile)
        try:
            output = io.StringIO()
            
            with contextlib.redirect_stdout(output):
                execute(args, doc)
                print("[VPYPE_INFO]" + str(output.getvalue()) )
                print("vpype read " + filename + " " + args)

            socketio.emit('status_log', {'data': 'File converted.'})
            return 'Exported ' + str(outputFile)
        except Exception as e:
            socketio.emit('status_log', {'data': 'File not converted. ' + str(e)})
            print("\033[91m[VPYPE_ERROR]\033[0m" + str(e))
            # Do Not change the sart sting " File not converted"
            return 'File not converted. ' + str(e)
