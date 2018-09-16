#Kill anything running in the 5000 port
fuser -n tcp -k 5000

#export and run the App
export QUART_APP=QuartApiAssincrona.py
quart run