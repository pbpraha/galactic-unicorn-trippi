# galactic-unicorn-trippi
Trippy effects with WIFI control and presets



https://user-images.githubusercontent.com/4026146/226233938-0212d378-c3eb-4a63-b759-0cc3abc9a344.mov

----------------

Based on this example by Pimoroni\
https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/galactic_unicorn/numpy/trippy.py

Using server code from here\
https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/galactic_unicorn/galactic_paint


## CAUTION!
*This code let's you strobe your Galactic Unicorn.*

*Be careful if you or others around you are photosensitive.*

## Setting Up
You'll need `WIFI_CONFIG.py` in the root of the Pico. 

Open up `WIFI_CONFIG.py` in Thonny to add your wifi details (and save it when you're done).

You will also have to install `micropython-phew` and `microdot` through Thonny's Tools -> Manage Packages.

Run `trippy_web_ui.py` through Thonny and it should get connected and give you a URL to visit. 

Open that URL in your browser and start tripping!

![image](https://user-images.githubusercontent.com/4026146/226232542-d60a634b-2e69-415b-9519-3ceab17fea5b.png)

## Note:
If you are using Firefox you may not be able to connect to the GU as Firefox insists on trying to connect via **https**.

If you have a similar problem then I suggest trying a different browser, e.g. Chrome
