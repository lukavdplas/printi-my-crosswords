# printi-my-crosswords
Send crosswords to a thermal printer!

### Details
This module imports the xml crosswords as exported by my [crossword generator](https://github.com/lukavdplas/crossword-maker). It then converts the crossword and the clues to a bitmap image using Pillow, and sends it to a thermal printer with printi software, using the [printipigeon](https://github.com/fonsp/printi-pigeon) module.

### Picture!
![thee pictures showing a receipt with a crossword on it coming out of a printer, being held up to the camera and being filled in](docs/demonstration.jpg)

### Future improvements
The program works well right now. Some things I may want to add in the future:
* wrap text for descriptions (most descriptions are so short it is not necessary, but just in case).
* add a solution print function.
