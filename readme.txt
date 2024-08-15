



MTF unpacker/packer for Darkstone archives.


-----------------------------------------------
How to use:
-----------------------------------------------

Note: You can drag and drop the .mtf file onto mtf.exe to unpack the file.

Examples for cli:

to unpack:
mtf -x -i data.mtf -o ./extracted

to pack:
mtf -a -i data.mtf -o ./source_directory

to save a list:
mtf --list -i data.mtf -l data.mtf.txt


-----------------------------------------------
About:
-----------------------------------------------

This script is a reimplementation of "darkstone-tools" (by Game3DEE) to Python.

The advantages are:

a) do not require NodeJS
b) standalone and portable
c) standard command-line arguments similar to 7z and ffmpeg.
d) easier to use (support drag'n'drop) and modify


Note: Compression is also not supported for new archives since there are not a lot of info about it was availible.


-----------------------------------------------
System Requirements:
-----------------------------------------------

Win7 x86 or newer (PythonWin7 was 3.12.3 used, can require KB2533623)














-----------------------------------------------
Usage:
-----------------------------------------------

Usage: mtf COMMAND [OPTIONS]
Example: mtf -x -i data.mtf -o ./extracted


Commands:

-a, --add, create
-x, --extract, extract
-l, --list, list
Create a new MTF file from the specified input.
Extract files from an MTF to a specified directory.
List the contents to a file (use with -l option)
            
       
     
Options:

-i, --input
-o, --output
-l
Specify the input MTF file.
Specify the output directory.
Specify the output file for list of content.
              

Examples:

  mtf --add -i data.mtf -o ./source_directory
  mtf --extract -i data.mtf -o ./extracted
  mtf --list -i data.mtf -l list.txt

Note: Replace 'COMMAND' with '--add', '--extract', or '--list' and provide the necessary options.


-----------------------------------------------
Authors:
-----------------------------------------------


Based on reasearches of many open-source contributors.


"MTF unpacker/packer for Darkstone" is open-source, so you're free to modify the code as needed. 
License: CC0



- downloaded from oketado.ru, 2024 -
