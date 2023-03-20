# galactic-unicorn-trippy
Trippy effects with control over WIFI

Based on this example by Pimoroni\
https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/galactic_unicorn/numpy/trippy.py

Using server code from here\
https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/galactic_unicorn/galactic_paint


## CAUTION!
This code let's you strobe your Galactic Unicorn.
Be careful if you or others around you are photosensitive.

## Setting Up
You'll need `WIFI_CONFIG.py` in the root of the Pico. 

Open up `WIFI_CONFIG.py` in Thonny to add your wifi details (and save it when you're done).

You will also have to install `micropython-phew` and `microdot` through Thonny's Tools -> Manage Packages.

Run the example through Thonny and it should get connected and give you a URL to visit. Open that URL in your browser and start painting!

## Running
Run the script in Thonny.
If you have set up your WIFI correctly you should see the Pico's IP address in the Shell window

![image](https://user-images.githubusercontent.com/4026146/226232542-d60a634b-2e69-415b-9519-3ceab17fea5b.png)

Visit the IP and wait for the UI to connect.

