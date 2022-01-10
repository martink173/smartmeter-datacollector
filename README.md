# Smart Meter Data Collector for Energienetze Steiermark L+G e450

This is a forked and modified version of [Smartmeter Datacollector](https://github.com/scs/smartmeter-datacollector) which contains adaptations to read Landis+Gyr e450 smart meters provided by [Energienetze Steiermark](https://www.e-netze.at/) in Austria. For general usage and instructions please see the Smartmeter Datacollector GitHub page.

The following modifications were made:
* Support of Landis+Gyr E450:
  * Parse decrypted push messages
  * Pushed OBIS codes added
  * Generate data point objects
* Support for [Volkszaehler](http://www.volkszaehler.org) added
  * Example data sink for positive/negative instantaneous power added

The E450 smart meter was connected to a RaspberryPi using the provided customer interface and a BELTI USB-to-MBUS-slave module.

The following data is pushed (OBIS codes):
* 1.0.1.8.0.255
* 1.0.1.8.1.255
* 1.0.1.8.2.255
* 1.0.1.7.0.255
* 1.0.2.8.0.255
* 1.0.2.8.1.255
* 1.0.2.8.2.255
* 1.0.2.7.0.255
* 1.0.3.8.0.255
* 1.0.3.8.1.255
* 1.0.3.8.2.255
* 1.0.3.7.0.255
* 1.0.4.8.0.255
* 1.0.4.8.1.255
* 1.0.4.8.2.255
* 1.0.4.7.0.255

Tested with Python 3.9.

# Acknowledgements
The initial `smartmeter-datacollector` and its companion project [`smartmeter-datacollector-configurator`](https://github.com/scs/smartmeter-datacollector-configurator) have been developed by **[Supercomputing Systems AG](https://www.scs.ch)** on behalf of and funded by **[EKZ](https://www.ekz.ch/)**.
