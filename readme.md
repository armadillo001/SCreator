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
Please login the S Creator platform and copy your session cookie to confidential/session.ini, the session cookie can be found on your profile page (click the top right corner of your profile).

#### 1. Setup config.ini ####

config.ini: save all the meta data of data-streams, when you add a new data-stream, please set up the config.ini file
so that the system will create and upload it to the platform automatically. After you setup the indicator, please make
sure you have the right loader file defined in 'loader/' directory. 

#### 2. Define a loading method ####

loader/YOURMETHOD.py: it includes important functions regarding how to download and process the files. The name of the
file should be STRICT the name of the indicator you defined in the config.ini file. Otherwise the system cannot find it.

#### 3. Run the main function daily ####

We assume the creator of the data function will maintain the data stream in S-creator everyday so that others can use it. So a good idea
would be to schedule the main.py task using something like "crontab" (in Linux and Mac) in your local system.  


