This is a brainstorming file where to put your immagination about the possible future evolution of this project.

1) AI adoption
    a) AI hardware selection
    b) AI engine selection
    c) AI training needed?

2) Mesh network configuration

3) Solar panel integration

4) Is it worth to have the Micro:bit out of this project, or there could be some hidden benefits?
    a) How do you think about having Micro:bit as an optional device? Wireless connected via serial-bluethoot to the Raspberry, only to issue command to this one? 
    b) Is it worth to use PIR sensor instead of the SONAR one, and connect it directly to the Raspberry?

5) Are terminal based (text) images possible to inject as AI training? ASCII Art convertion could help reduce the complexity of the AI model and calculations?

6) Ham radio SSTV mode as a new option for sending images
    a) There is a Python module which enable image transformation into wav files
       The generated audio can be sent as a modulated FM signal over the antenna using PiFM 
       git clone https://github.com/dnet/pySSTV
       cd pySSTV ; python3 ./setup.y build ; sudo python3 ./setup.py install
       cd <where images are> ; python3 -m pysstv --mode MartinM2 --resize image.png output.wav 
       a file of 35Kb result in an audio wav file of about 5.5 Mb.
    b) Raspberry pi is able to send FM mofulation as RF via a small antenna connected to the GPIO4
       git clone https://github.com/F5OEO/rpitx
       cd rpitx ; ./install.sh (the compile process somehow fail to compile some programs but we need the pifmrds which is orrectly available)
       reboot
       sudo ./pifmrds -freq 76 -audio /home/ilfarodargento/sent/pettirosso-inverno.wav

...possibile utilizzo anche per le radiosonde che potrebbero inviare immagini
        
