# CheapTalk

This project implements a server for a retro-style messaging application built using Python.


## Course & University
ECE 4564 - Virginia Tech


## Running via Local Python

  
Assuming that you have a Python 3 environment installed locally, you can run the server using a terminal window. After cloning the repo, navigate to the **src/** directory using the following the command

```
cd src
```

###  Run the Server

Run the server by specifying the port on which the server process should listen.

 
```
python3 -m chat_server {IP_ADDRESS}
```

  

If you wish to run using the local IP address, run the following command to find the IP address

```
ipconfig
```

##  Running via Docker

  

You can also run the server processes using Docker.

  

###  Build the Container Image

  

Open a terminal and make the directory containing this README the shell's

current directory. Then run the following command to build the image.

  

```
docker image build --tag cheap_talk .
```

###  Run the Server Container

  

Start the server container using the following command.

  

```
docker run -it cheap_talk
```

##  Credits

- Source code for the client was provided by Professor Carl Harris.

- Project description, design blueprint, and protocol specifications were provided by Professor Carl Harris.


##  Developers
- Ahmed Fathi
- Yaseen Ahmed
- Ryan Phillips



