# File Sharing System
Computer Networks project
written in Python

## Introduction
This is a file sharing platform.

    Watchdog module to monitor changes in the folder.
    support for multiple diffrent clients.
    support for multiple diffrent sessions within a client.
    
 ### Client-Side
 
#### Connection initialization:
The client is being initialized; a client should provide five arguments:
1. `IP` - server's IP.
2. `PORT` - server's port.
3. `PATH` - path to the synchronized folder.
4. `TIME` - desired interval for an update.
5. `ID` - client's ID

The method `connect_to_server`:
The method will check if a client has provided an ID; if so, the client will send a pull request to the server requesting the files stored on the server.
o.w a new client will be initialized, and the server will send a push request to the server resulting in an upload of the provided folder.

#### Synchronazation with the server:
`check_for_updates` method:
check_for_updates - method is in-charge of notifying a server an update is needed with the current client, happens each `TIME` interval, or is triggered by the watchdog module.

There are several different sanarios:
1. `created` - new file is transmitted from client to server.
2. `moved` - new folder is transmitted from client to server.
3. `deleted` - a delete request of a folder or a file is transmitted to the server. 



#### WatchDog Module:
    Python API and shell utilities to monitor file system events.
  The watchdog module monitors the provided folder and notifies the server about a change that occurred in the folder.
  For every change that occured in the folder, the client will notify the server of the difference with the commands defined above.
  
 ### Server-Side
 
 #### Connection initialization:
The server receives a connection from the client and passes the `client-id` provided.
If the ID provided is invalid, the server generates a new client on the cloud and transmits the generated ID back to the client for future connections.
 
