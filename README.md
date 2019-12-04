# Graceful Shutdown
Powerdown gpio and LED stripes slowly and in a specific order.

- Power down (gpio) lights
- Power down amplifiers
- Power down screens
- Power down sound rack (after amplifier to avoid peak sound)

Then slowly fade out LEDs
