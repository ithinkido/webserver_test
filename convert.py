import os 
import subprocess

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)

socketio = SocketIO(app)

def convert_file(file, outputsize = 'a4',  pageorientation = 'landscape', device = 'hp7475a', speed = '', custom_comand = '', linemerge  = '', linesort = '', linesimplify = '', reloop = ''):
    if file:
        print('Converting file: ' + file)

        filename, file_extension = os.path.splitext(file)
        vpype_options =""
        args = 'sudo vpype';
        args += ' read "' + os.getcwd() + '/' + str(file) + '"'; #Read input svg

        # Scale svg to desired paper size
        if (pageorientation == 'landscape'):
            args += ' eval w,h=gprop.vp_page_size crop 0 0 %w% %h% rect -l1000 0 0 %w% %h% layout -l -m  0 ' + outputsize + ' ldelete 1000';

        else:
            args += ' eval w,h=gprop.vp_page_size crop 0 0 %w% %h% rect -l1000 0 0 %w% %h% layout -m  0 ' + outputsize + ' ldelete 1000';

        # Vpype optimise 

        if custom_comand :
            vpype_options += " " + custom_comand ;

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

        output = subprocess.getoutput(args)

        if ("Error" in output):
            output = output.partition("Error:")[2]
            socketio.emit('status_log', {'data': 'File not converted.'})
            socketio.emit('status_log', {'data': output})
            return 'File not converted.'
        else:
            socketio.emit('status_log', {'data': 'File converted.'})
            return 'Exported ' + str(outputFile)
