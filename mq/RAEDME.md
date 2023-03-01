# 3010MQ
#### Run 3010MQ
1. Run server

    Option 1: ```python server.py```
    
    Option 2: ```python server.py <_client port_> <_worker port_>```
    
    Option 3: ```python server.py <_client port_> <_worker port_> <_server IP_>```
    

2. Run client

   Option 1: ```sh loader.sh 8001```
   
   Option 2: ```sh loader.sh <_client port_>```
   
    **Note: <_client port_> and <_server IP_> need to be same as the one entered to run server**

3. Run worker

   Option 1: ```python worker.py```
   
   Option 2: ```python worker.py <_server IP:worker port_> <_outputs port_> <_syslog port_>```
   
    **Note: <_server IP:worker port_> needs to be same as the ones entered to run server**

4. Run monitor to check job status

    Option 1: ```python status.py```
    
    Option 2: ```python status.py <_client port_>```
    
    Option 3: ```python status.py <_client port_> <_server IP_>```
    
    **Note : <_client port_> and <_server IP_> need to be same as the one entered to run server**
    
#### Default Ports
- ```<_client port_>```: 8001

- ```<_worker port_>```: 8002

- ```<_server IP_>```: localhost

- ```<_outputs port_>```: 30000

- ```<_syslog port_>```: 30001
