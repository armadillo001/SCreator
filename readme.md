## Upload data stream to S-Creator ##

Here comes an easy to use package to upload processed financial indicator as a data stream to S-creator platform. 
The data stream's format should be stirctly defined as a time-series saved in panda dataframe - timestamps are saved as indices,
values are saved as "signal" columns. Please find an example in the data folder. 

### How it works ###
For each indicator defined in config.ini:
* Parse the configuration file and create a Stream class.
* Download the indicator based on the function fun_load_data() defined in "loader/IndicatorName"
* Process the indicator based on the function fun_compute_data() defined in "laoder/IndicatorName", save the historic values in "data/init_with/" and the most recent value in "data/on_going/" directory respectively.
* If the indicator has not been uploaded to S-creator as data-stream, create the data-stream for the indicator in S-Creator and upload its historic values to S-Creator.
* Upload the most recent value of the indicator to S-creator
* Save the models status to "states/indicator_states.csv"
* Save the log file to "log/"

### Key steps ###
#### 0. Update your session cookie ####
Please login the S Creator platform and copy your session cookie to confidential/session.ini, 
the session cookie can be found on your profile page (click the top right corner of your profile and please find the Session ID as the followed image).
![image1](https://user-images.githubusercontent.com/16822689/178646114-94f23de9-a78c-4e5c-8104-2e5622932fd1.png)

#### 1. Setup /config.ini ####
Please find "config.ini" file in the root directory, save all the information (meta data) of data-streams, 
when you add a new data-stream, please set up the config.ini file so that the system will create and upload it to the 
platform automatically. You can refer to the example. After you setup the indicator, please make sure you have the right 
loader file defined in 'loader/' directory. For each indicator, you need to have a seperate file with the same indicator 
name defined in "loader/" directory.

* description: a short description about the indicator
* authors: ID of the contributors, can be obtained from the user profile page (click the top right of user profile),
multiple authors are seperated by comma ","
* datestart: an optional string help to define the starting date of the indicator
* target: the asset that the indicator can be used to project, note that the asset need to be available in the system
* pctgs: percentage of each contributor's contribution, seperate by "," (for example: a0dfcacGPnNUa5yGys7Xfacv9q1, a0c4cacKJnO0bAyGcc0Xabc31g1)
* range: a value ranged from 0 to 4, used for future indicator categorization (0: unknown, 1: predict tomorrow, 2: up to one week, 
3: up to two weeks, 4: up to a month).

#### 2. Define a loading method ####
loader/YOURMETHOD.py: it includes important functions regarding how to download and process the files. The name of the
file should be STRICT the name of the indicator you defined in the config.ini file. Otherwise the system cannot find it.
Please refer to the examples we saved in this directory.

#### 3. Run the main function daily ####
We assume the creator of the data function will maintain the data stream in S-creator everyday so that others can use it. 
So a good idea would be to schedule the main.py task using something like "crontab" (in Linux and Mac) in your local system.  


