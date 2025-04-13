# Assignment 1

There are two programs:
1. Basic LFSR
2. General LFSR

## Basic LFSR

It will print 20 bits sequence of LFSR operation on 4 bits binary (0b0110) with tap sequence of 0b1001:
```
python Assignment\ 1/basic_lfsr.py 
```
## General LFSR

In principle, the xor operation and the test is similar with the basic. 
But, it affords any register size. 
```
python Assignment\ 1/basic_lfsr.py 
```

# Assignment 2

## Run with docker instance

Cd into the warehouse app
```
cd Assignment\ 2/
```

Build the image
```
docker build -t warehouse .
```

Run the docker instance
```
docker run -p 8000:8000 warehouse
```


## Run with python
Execute shell script to install python requirements and run the db migrations.

Run the script with python version ^3.13

```
./bootstrap
```

```
python manage.py runserver
```

