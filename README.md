# Documentation
## Software Requirements
- Docker
- Docker Compose
- Traefik
- (A domain that will resolve to the machine's IP, specifically at the api.* subdomain using an A record; In this case the compose contains the actual)
## Security and authentication
Every post request received by  `<domain>/post/` will need to contain an Authentication header, containing a bearer toker (JWT).
This will allow the board to authenticate itself to the server, matching if its name is present in the accepted boards and at the same time, it will guarantee the authenticity of the client, that will be asked to send a signature formed in a specific way.
The signature will contain a mix of hash keys and sent by the POST request according to specific policies.
The same policies will be applied by the board to allow the request to be accepted.
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
