# Documentation
## Software Requirements
- Docker
- Docker Compose
- Traefik
- (A domain that will resolve to the machine's IP, specifically at the api.* subdomain using an A record; In this case the compose contains the actual)
## Routes
The service listens and responds to the following routes
- `POST <domain>/post/` insert light, temperature, humidity and the timestamp(in seconds) into the DB; The payload needs to be structure as follows `{temperature:number,humidity:number,light:number,time:numer}` (if the data sent doesen't respect the provided format the endpoint will respond with code `400`
- `GET <domain>/boards` returns a list of the boards accepted as follows `[<board name>,<board name>,...]`
- `GET <domain>/current` returns the current (or last sent) data of all the boards as follows `[{name:<board-name>, data:{temperature:number,humidity:number,light:number,time:numer},...]`
- `GET <domain>/history` returns the history of the data of all the boards (going back to 10 hours from the request time) as follows `[{name:<board-name>, history:[{time:numer,data:{temperature:number,humidity:number,light:number},...]},...]`
- `GET <domain>/current/<board name>` returns the current (or last sent) data of the speciefied board (if present in `<domain>/boards`) as follows `{name:<board-name>, data:{temperature:number,humidity:number,light:number,time:numer}`
- `GET <domain>/history/<board name>` returns the history of the data the specified board (going back to 10 hours from the request time, if present in `<domain>/boards`) as follows `{name:<board-name>, history:[{time:numer,data:{temperature:number,humidity:number,light:number},...]}`
## Security and authentication
Every post request received by  `<domain>/post/` will need to have an Authentication header, containing a bearer toker (**[JWT](https://jwt.io/)**). \
This will allow the board to authenticate itself to the server, matching if its name is present in the accepted boards and at the same time, it will guarantee the authenticity of the client, that will be asked to send a signature formed in a specific way. \
The signature will contain a mix of hash keys and sent by the POST request according to specific policies. \
The same policies will be applied by the board to allow the request to be accepted. \
\
Missing any of the requirements above will result in response with code `403`. \
\
*For exammple on this repo the policies are  `<header> + time + <trailer>`. This of course works just as an exaple and in the final project both the policies and the hashes will be different*
# Application Stack
## [Frontend](https://github.com/ThaTeo/scudo-reloaded-frontend)
Hosted with Firebase Hosting
- TypeScript React (Create React App)
- Chakra UI
## [Backend](https://github.com/ThaTeo/esp-backend)
A container running on a VPS with Traefik  
- Flask (Python)
- Firebase API
## [Hardware](https://github.com/ThaTeo/esp-script)
- Esp32 WROOM (Espressif dev kit C)
- DHT 11
- Photoresistor
## [Database](https://firebase.google.com/docs/firestore)
- Cloud Firestore
