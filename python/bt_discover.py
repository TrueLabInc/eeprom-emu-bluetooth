def search():
   while True:
      devices = bluetooth.discover_devices(lookup_names = True)
      for x in devices: # <--
         print x        # <--

search()
