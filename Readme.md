### main_api
a simple flask api


### simple_client



#### utils

##### Cabinet




###### Notes:
1. At the moment the socket client receives the data and appends it to cabinet.received_data, the cabinet is running watcher on a new thread
  - watcher checks the lenght of the training data and saves the file whe the lenght is greater than the value provided by split_at
  - Altough watcher is a function of Cabinet it runs on a new thread and there are no precautions being used when acessing the data in the main thread
  - At the moment this has not given any problems, however this should be looked into
2. The current implementation is the server resides on the machine capturing the data and this client on any other machine on the network
  - This means that multiple clients can receive data but not the other way around
  - So maybe this should be a simple_server and the client reside on the machine that captures training data
